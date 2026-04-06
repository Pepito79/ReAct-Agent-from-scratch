from pydantic import BaseModel
from enum import Enum
from typing import Callable , List , Optional


class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"
    OBSERVATION = "observation"
    RESUME = "resume"
    ASK_HUMAN ="ask_human"
    
class Message(BaseModel):
    type : MessageType
    content: str
    
    def to_openai_format(self):
        if self.type in [MessageType.USER , MessageType.OBSERVATION]:
            return {"role":"user" , "content":self.content}
        else:
            return {"role":"assistant" , "content": self.content}
 
class ToolParameter(BaseModel):
    name: str
    type: str                    
    description: str
    required: bool = True       
    
class Tool(BaseModel):
    name: str
    function: Callable
    description: str
    parameters: List[ToolParameter] = []
    example : Optional[str] = None
    
    
""" 
tool1 = {
    
    name : "tool1", 
    function: func, 
    descruption: "cette fonction retourne 1",
    parameters: [ ToolParameter("a",int,"num1",true)]
}


"""