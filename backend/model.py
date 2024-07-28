from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from dotenv import load_dotenv
from datatypes import TextIn, Nutrients, Sentence, FinalResponse
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

final_schema = ResponseSchema(
    name="final_output", description="Final output of the model"
)

output_parser2 = StructuredOutputParser.from_response_schemas([final_schema])

format_instructions2 = output_parser2.get_format_instructions()

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-pro"
)


def get_response(food_name: TextIn):
    prompt_nutrients = """
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
            template=prompt_nutrients,
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


def get_final_response(nutrients: Nutrients):
    prompt_final = """
    For the given nutrients of the specific food tell me how good is this for health \
    how frequently it can be consumed,and is there any bad impact on our health \
    the answer should not be more than 2 sentence, try to give answer in a creative sentence\
    ```{nutrients}```

    ```{format_instructions2}``   
    """
    try:
        prompt = PromptTemplate(
            template=prompt_final,
            input_variables=["nutrients"],
            partial_variables={"format_instructions2": format_instructions2},
        )

        chain = prompt | llm
        output = chain.invoke({"nutrients": nutrients})
        result = output_parser2.parse(output.content)
        response = Sentence(response=result["final_output"])
        return response
    except Exception as e:
        print(f"An error occurred: {e}")


def get_extracted_details(food_name: TextIn) -> FinalResponse:
    nutrients = get_response(food_name)
    body = Nutrients(
        name=nutrients.name,
        proteins=nutrients.proteins,
        fats=nutrients.fats,
        carbohydrates=nutrients.carbohydrates,
        vitamins=nutrients.vitamins,
        minerals=nutrients.minerals,
    )
    sentence = get_final_response(body)
    return body, sentence
