from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from dotenv import load_dotenv
from datatypes import TextIn
import os

load_dotenv()

name_schema = ResponseSchema(name="name", description="name of the food")
pros_schema = ResponseSchema(name="pros", description="advantages")
cons_schema = ResponseSchema(name="cons", description="disadvantages")

response_schema = [name_schema, pros_schema, cons_schema]
output_parser = StructuredOutputParser.from_response_schemas(response_schema)

format_instructions = output_parser.get_format_instructions()


class Dietinfo(BaseModel):
    name: str
    pros: str
    cons: Optional[str]


# def get_user_input():
#   return input("Name the food you want to know about: ")


def get_response(food_name: TextIn) -> Dietinfo:
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-pro"
    )
    # parser = PydanticOutputParser(pydantic_object=Dietinfo)
    prompt_template = """
    You are expert in answering the pros and cons of the fruits and vegetables \
    you are given by food name and you will output name of food, its pros and cons \

    ```{food_name}```

    {format_instructions}
  """

    try:
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["food_name"],
            partial_variables={"format_instructions": format_instructions},
        )

        chain = prompt | llm
        output = chain.invoke({"food_name": food_name})
        result = output_parser.parse(output.content)
        for key, value in result.items():
            result[key] = value.replace("\n*", "")
        response = Dietinfo(
            name=result["name"], pros=result["pros"], cons=result["cons"]
        )
        return response.json()
    except Exception as e:
        print(f"An error occurred: {e}")
