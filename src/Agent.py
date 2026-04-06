from dotenv import load_dotenv
from utils.types import Tool, ToolParameter,Message,MessageType
from typing import Any , Dict ,List, Callable
from utils.utils import extract_params_types
import re
import json

class Agent:
    
    def __init__(self, client : Any ,system_prompt: str | None = None , stream : bool = True):
        
        load_dotenv()
        if not client:
            raise Exception("Enter a  valid client before using the Agent")
        
        self.system_prompt = system_prompt or "Tu es un agent ReAct intelligent et utile"
        self.client = client
        self.tools : Dict[str,Tool] = {}
        self.tool_descriptions : List[Dict] = []
        
        #Let's add some memory to our agent
        self.messages  : List[Message] = []
        self.max_history = 12
        self.tokens_outputed = 0
        self.stream = stream
        
    def execute(self) -> Dict:
        """Call the LLM

        Returns:
            str: the llm answer
        """
        if len(self.messages) > self.max_history:
            print("Historic too long , summary process started ....")
            summary_text = self.summarize_history()
            
            if summary_text:
                self.messages = [
                    Message(type=MessageType.RESUME, content=f"RESUME: {summary_text}")
                ] + self.messages[-6:]
                
                
        messages = [{"role": "system", "content": self._build_system_prompt()}]
        messages.extend([m.to_openai_format() for m in self.messages])
        
        response  = self.client.chat.completions.create(
            model="deepseek/deepseek-chat",   
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream = True
        )
        full_response = ""
        if self.stream:
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    print(content, end="", flush=True)   

            print("\n")  # Retour à la ligne à la fin
            return {"response": full_response, "tokens": 0} 
        
        else:
            response  = self.client.chat.completions.create(
            model="deepseek/deepseek-chat",   
            messages=messages,
            temperature=0.7,
            max_tokens=4096,
            stream = False
        )
        answer : str = response.choices[0].message.content
        tokens : int = response.usage.completion_tokens
        self.tokens_outputed += tokens
        return {"response": answer , "tokens": tokens}
    
    def get_total_tokens(self):
        return f"The model has outputed {self.tokens_outputed} tokens since the beginning !"
    
    def summarize_history(self):
        """ Use an llm to resume the conversation""" 
        
        old_messages = self.messages[:-6]
        if not old_messages:
            return ""
        
        history_text = "\n".join([
            f"{msg.type.value.upper()}: {msg.content}" 
            for msg in old_messages
        ])   
        
        #Prompt to say to the llm to resume the context
        summary_prompt = f"""You are a highly skilled conversation summarizer.

Create a clear and concise summary of the previous conversation. Include only the essential information:

- User details and preferences
- Main goals and objectives
- Important facts and context
- Any decisions or conclusions reached

Conversation to summarize:
{history_text}

Return ONLY the summary. No introductions, no explanations, no extra text."""
        try:
            response = self.client.chat.completions.create(
                model="deepseek/deepseek-chat",          
                messages=[{"role": "user", "content": summary_prompt}],   
                temperature=0.5,
                max_tokens=350,
            )
            summary = response.choices[0].message.content.strip()
            print("[SUMMARY GENERATED]")
            return summary
        
        except Exception as e:
            print(f"Error while summarizing the messages : {e}")
            return "Previous conversation summary not available."

    def add_tool(self, func: Callable, description: str | None= None, example: str | None = None):        
        # Extraction of the function name
        tool_name: str  = func.__name__
        
        # Description of the tool
        desc = description or func.__doc__ or f" Call the function {tool_name}"
        # Verify if the tool is already present
        if tool_name in self.tools:
            return "[WARNING] Tool already present !"
        #Add the parameters of the tool
        types_params = extract_params_types(func)
        param_list: List[ToolParameter] = []
        for param_name, param_type in types_params.items():
            param_list.append(
                ToolParameter(
                    name=param_name,
                    type=param_type,
                    description="",           
                    required=True             
                )
            )
        #Add the tool to the agent
        self.tools[tool_name] = Tool(
            name= tool_name,
            function = func,
            description= desc,
            parameters=  param_list,
            example=example
        )
        #Add the tool description
        self.tool_descriptions.append(
            {
                "name": tool_name,
                "description": desc
            }
        )
        print(f"[TOOL]: The tool {tool_name} has been added to the agent !")
        
        
    def execute_tool(self, tool_name:str , tool_input: Any) -> str:
        """Executes in the computer the tool wanted by the llm to detect if it is a final answer , a thought or an action

        Args:
            tool_name (str): tool name
            tool_input (Any): parametrs of the tool 

        Returns:
            str: the answer
        """
        
        
        #Verify if the tool exists
        if tool_name not in self.tools:
            return f" [HALLUCINATION] The LLM called {tool_name} : a tool that does not exists"
        
        try:
            tool = self.tools[tool_name]
            func = tool.function
            
            if isinstance(tool_input,dict):
                result = func(**tool_input)
            elif isinstance(tool_input, str):
                if len(tool.parameters) == 1:
                    param_name = tool.parameters[0].name
                    result = func(**{param_name: tool_input})
                else:
                    result = func(tool_input)
            else:
                result = func(tool_input)

            return str(result)
        
        except Exception as e:
            return f"[TOOL ERROR] Error while execution the tool '{tool_name}': {str(e)}"  

    def _parse_response(self, text: str) -> dict:
        text = text.strip()
        #Extraction of the thought
        thought_match = re.search(r'Thought[:\s]*(.*?)(?=Action:|Final Answer:|$)', 
                                  text, re.DOTALL | re.IGNORECASE)
        thought = thought_match.group(1).strip() if thought_match else ""

        # Detection of the final answer
        final_match = re.search(r'Final Answer[:\s]*(.*)', text, re.DOTALL | re.IGNORECASE)
        if final_match:
            return {
                "type": "final", 
                "thought": thought,
                "content": final_match.group(1).strip()
            }

        # Detection of the action 
        action_match = re.search(r'Action[:\s]*(\w+)', text, re.IGNORECASE)
        if action_match:
            tool_name = action_match.group(1).strip()

            input_match = re.search(r'Action Input[:\s]*(.*)', text, re.DOTALL | re.IGNORECASE)
            input_str = input_match.group(1).strip() if input_match else ""

            input_str = re.sub(r'^(s:|json:|input:)\s*', '', input_str, flags=re.IGNORECASE).strip()
            try:
                if input_str.startswith('{') and input_str.endswith('}'):
                    tool_input = json.loads(input_str)
                else:
                    tool_input = input_str
            except:
                tool_input = input_str

            return {
                "type": "action",
                "thought": thought,
                "tool_name": tool_name,
                "tool_input": tool_input
            }
        
        return {
            "type": "text",
            "thought": thought,
            "content": text
        }
        
    
    def run(self,user_query:str, max_steps: int = 15) -> str:
        """ Run de agent 

        Args:
            user_query (str): the user query
            max_steps (int, optional): Number of maximum steps. Defaults to 15.

        Returns:
            str: The CoT and the agent's answer
        """
        print("=== ReAct Agent Started ===\n")
        
        #Add the query to the history
        self.messages.append(Message(type=MessageType.USER , content=user_query))
        for step in range(max_steps):
            print(f"== STEP : {step+1} ==\n")
            resp = self.execute()
            response_text = resp["response"]
            self.messages.append( Message( type= MessageType.AGENT , content= response_text))
            
            #Find the type of response
            parsed_resp= self._parse_response(response_text)
            if parsed_resp.get("thought"):
                print(f"THOUGHT ({resp["tokens"]} tokens):\n{parsed_resp['thought']}\n")
            
            if parsed_resp["type"] == "final":
                print(f"FINAL ANSWER :\n{parsed_resp['content']}\n\nFINAL ANSWER RETURNED AFTER {step+1} STEPS\n")
                return "=== END ==="
             
            elif parsed_resp["type"] == "action": 
                tool_name = parsed_resp["tool_name"]
                tool_input = parsed_resp["tool_input"]
                print(f"\nACTION :\nTOOL USED: {tool_name}\nTOOL INPUT:{tool_input}\n")
                
                #Let's execute the action 
                observation = self.execute_tool(tool_name,tool_input)
                print(f"OBSERVATION({resp["tokens"]} tokens):\n{observation}\n")  
                
                self.messages.append(Message(type=MessageType.OBSERVATION , content = f"Observation : {observation}"))
                
            else:
                print(f"TEXT RESPONSE:\n{parsed_resp.get('content',response_text)}")
            
        print("LIMIT OF STEPS REACHED")
        return "LIMITS OF STEPS REACHED WITHOUHT FINDING THE ANSWER "
    
    def _build_system_prompt(self) -> str:
        """Build a strict system prompt for ReAct behavior."""
        
        if not self.tool_descriptions:
            return self.system_prompt

        tools_text = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in self.tool_descriptions
        ])

        return f"""You are a ReAct agent. Your job is to solve the user's question by reasoning step by step and using tools when necessary.

    Available tools:
    {tools_text}

    You MUST strictly follow this response format:

    Thought: [Your detailed reasoning]
    Action: [exact tool name]
    Action Input: [arguments only - text or JSON]

    OR, when you have the final answer:

    Thought: [Your final reasoning]
    Final Answer: [complete natural answer to the user]

    Important rules:
    - Always start with "Thought:"
    - Never output anything before "Thought:"
    - Do not add explanations or extra commentary
    - Use tools only when needed
    - Be concise and precise"""
    
    def __call__(self, message: str | None = None) -> str:
        """
        Single-turn interaction with the agent.
        Use this when you want only one LLM call (no ReAct loop).
        """
        if not message:
            raise ValueError("Message cannot be empty when calling the agent.")

        self.messages.append(Message(type=MessageType.USER, content=message))
        result = self.execute()
        self.messages.append(Message(type=MessageType.AGENT, content=result["response"]))

        return result["response"]      
    
    def get_tools(self):
        return self.tools
    
    def get_history(self):
        return self.messages
    