# ReAct Agent

A ReAct agent built from scratch in Python.

## About

This project is an intelligent agent capable of reasoning step by step and using tools to answer questions. It follows the ReAct pattern (Thought → Action → Observation → Final Answer).

The goal was to implement an autonomous agent without relying on heavy frameworks, in order to deeply understand how it works internally.

## Features

- Full ReAct loop
- Modular tool system with automatic parameter extraction
- OpenRouter support (DeepSeek, Claude, Gemini, Llama…)
- Clear display of reasoning at each step
- Clean conversation history management

## Technologies

- Python 3
- OpenRouter
- Pydantic

## Usage Example

```python
agent.add_tool(get_weather)
agent.add_tool(calculate)

result = agent.run("What is the weather in Paris and calculate 25 × 18?")