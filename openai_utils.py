import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

def get_openai_client():
    """Initialize and return OpenAI client"""
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_chat_model():
    """Initialize and return LangChain chat model"""
    return ChatOpenAI(
        model="gpt-4-turbo-preview",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def get_structured_output_parser(pydantic_model):
    """Get JSON output parser for structured output"""
    return JsonOutputParser(pydantic_object=pydantic_model)

def create_prompt_template(template, input_variables, format_instructions):
    """Create a prompt template with format instructions"""
    return PromptTemplate(
        template=template,
        input_variables=input_variables,
        partial_variables={"format_instructions": format_instructions}
    ) 