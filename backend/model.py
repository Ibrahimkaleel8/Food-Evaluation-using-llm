from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from dotenv import load_dotenv
from datatypes import TextIn, Nutrients, Sentence, FinalResponse, NameResponse
from prompt import PROMPT_NAME, PROMPT_NUTRIENTS, PROMPT_SUMMARY
from config import *
import os
import json
import logging

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

name_schema = ResponseSchema(name=NAME, description="name of the food")
protein_schema = ResponseSchema(name=PROTEIN, description="protein of the food item")
fats_schema = ResponseSchema(name=FATS, description="fats of the food item")
carbohydrates_schema = ResponseSchema(
    name=CARBOHYDRATES, description="carbohydrates of the food item"
)
minerals_schema = ResponseSchema(name=MINERALS, description="minerals of the food item")
vitamin_schema = ResponseSchema(name=VITAMINS, description="vitamins of the food item")

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

type_schema = ResponseSchema(
    name=FOOD_TYPE, description="type of food, cooked, raw, not a food"
)

ingredient_schema = ResponseSchema(
    name=INGREDIENTS, description="ingredients used in the cooked food"
)

response_schema2 = [type_schema, ingredient_schema]

output_parser3 = StructuredOutputParser.from_response_schemas(response_schema2)

format_instructions3 = output_parser3.get_format_instructions()

response_schema3 = ResponseSchema(name=SUMMARY, description="Final output of the model")

output_parser2 = StructuredOutputParser.from_response_schemas([response_schema3])

format_instructions2 = output_parser2.get_format_instructions()

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv(GOOGLE_API_KEY), model=GEMINI_MODEL
)


def get_name_info(food_name: TextIn) -> NameResponse:
    try:
        prompt = PromptTemplate(
            template=PROMPT_NAME,
            input_variables=[FOOD_NAME],
            partial_variables={FORMAT_INSTRUCTIONS3: format_instructions3},
        )

        chain = prompt | llm
        result = chain.invoke({FOOD_NAME: food_name})
        content = result.content.strip("```json\n").strip("\n```")
        result_dict = json.loads(content)
        response = NameResponse(
            name=food_name,
            type=result_dict[FOOD_TYPE],
            ingredients=result_dict[INGREDIENTS],
        )
        logging.info(f"get_name_info result: {response}")
        return response
    except Exception as e:
        logging.error(f"An error occurred in get_name_info: {e}")


def get_nutrients(food_data: NameResponse) -> Nutrients:
    food_name = food_data.name
    ingredients = food_data.ingredients if food_data.ingredients else ""

    try:
        prompt = PromptTemplate(
            template=PROMPT_NUTRIENTS,
            input_variables=[FOOD_NAME, INGREDIENTS],
            partial_variables={FORMAT_INSTRUCTIONS: format_instructions},
        )

        chain = prompt | llm
        output = chain.invoke({FOOD_NAME: food_name, INGREDIENTS: ingredients})
        result = output_parser.parse(output.content)
        response = Nutrients(
            name=result[NAME],
            proteins=result[PROTEIN],
            fats=result[FATS],
            carbohydrates=result[CARBOHYDRATES],
            vitamins=result[VITAMINS],
            minerals=result[MINERALS],
        )
        logging.info(f"get_nutrients result: {response}")
        return response
    except Exception as e:
        logging.error(f"An error occurred in get_nutrients: {e}")


def get_summary(nutrients: Nutrients) -> Sentence:
    try:
        prompt = PromptTemplate(
            template=PROMPT_SUMMARY,
            input_variables=[NUTRIENTS],
            partial_variables={FORMAT_INSTRUCTIONS2: format_instructions2},
        )

        chain = prompt | llm
        output = chain.invoke({NUTRIENTS: nutrients})
        result = output_parser2.parse(output.content)
        response = Sentence(response=result[SUMMARY])
        logging.info(f"get_summary result: {response}")
        return response
    except Exception as e:
        logging.error(f"An error occurred in get_summary: {e}")


def get_extracted_details(food_name: TextIn) -> FinalResponse:
    is_foodname = get_name_info(food_name)

    food_data = NameResponse(
        name=is_foodname.name,
        type=is_foodname.type,
        ingredients=is_foodname.ingredients,
    )

    if food_data.type != NOT_A_FOOD:
        nutrients = get_nutrients(food_data)

        body = Nutrients(
            name=nutrients.name,
            proteins=nutrients.proteins,
            fats=nutrients.fats,
            carbohydrates=nutrients.carbohydrates,
            vitamins=nutrients.vitamins,
            minerals=nutrients.minerals,
        )
        sentence = get_summary(body)
        logging.info(f"get_extracted_details result: {food_data}, {body}, {sentence}")
        return food_data, body, sentence
    else:
        logging.info(f"{food_name} is not a food")
        return None
