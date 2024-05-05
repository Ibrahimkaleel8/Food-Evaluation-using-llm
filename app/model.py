from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os
load_dotenv()

class Dietinfo(BaseModel):
  name: str
  pros: str
  cons: str

# def get_user_input():
#   return input("Name the food you want to know about: ")

def get_response(food_name):
    llm = ChatGoogleGenerativeAI(google_api_key = os.getenv('GOOGLE_API_KEY'), model="gemini-pro")
    parser = PydanticOutputParser(pydantic_object=Dietinfo)
    prompt_template = """
    You are expert in answering the pros and cons of the fruits and vegetables \
    you are given by food name and you will output name of food, its pros and cons \

    ```{food_name}```

    {format_instructions}
  """


    try:
        prompt = PromptTemplate(
        template = prompt_template,
        input_variables = ['food_name'],
        partial_variables={"format_instructions": parser.get_format_instructions()}
        )

        chain = prompt | llm
        output = chain.invoke({"food_name" : food_name})

        result = parser.parse(output.content)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        





