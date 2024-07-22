from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from dotenv import load_dotenv
from datatypes import TextIn, Nutrients
import os

load_dotenv()

name_schema = ResponseSchema(name="name", description="name of the food")
protein_schema = ResponseSchema(name="protein", description="protein of the food item")
fats_schema = ResponseSchema(name="fats", description="fats of the food item")
carbohydrates_schema = ResponseSchema(
    name="carbohydrates", description="carbohydrates of the food item"
)
minerals_schema = ResponseSchema(
    name="minerals", description="minerals of the food item"
)
vitamin_schema = ResponseSchema(
    name="vitamins", description="vitamins of the food item"
)

response_schema = [
    name_schema,
    protein_schema,
    fats_schema,
    carbohydrates_schema,
    minerals_schema,
    vitamin_schema,
]
output_parser = StructuredOutputParser.from_response_schemas(response_schema)

format_instructions = output_parser.get_format_instructions()


def get_response(food_name: TextIn):
    llm = ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-pro"
    )

    prompt_template = """
    You are an expert Nutritionists, i will provide you with food_name, Please provide information \
    on the total following nutrients found in food_name.

    NUTRIENTS:
    1.proteins
    2.fats 
    3.carbohydrates 
    4.vitamins 
    5.minerals
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

        response = Nutrients(
            name=result["name"],
            proteins=result["protein"],
            fats=result["fats"],
            carbohydrates=result["carbohydrates"],
            vitamins=result["vitamins"],
            minerals=result["minerals"],
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")
