from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import ResponseSchema
from langchain.output_parsers import StructuredOutputParser
from dotenv import load_dotenv
from datatypes import TextIn, Nutrients, Sentence, FinalResponse, NameResponse
import os
import json

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

type_schema = ResponseSchema(
    name="food_type", description="type of food, cooked, raw, not a food"
)

ingredient_schema = ResponseSchema(
    name="ingredients", description="ingredients used in the cooked food"
)

response_schema2 = [type_schema, ingredient_schema]

output_parser3 = StructuredOutputParser.from_response_schemas(response_schema2)

format_instructions3 = output_parser3.get_format_instructions()

response_schema3 = ResponseSchema(
    name="final_output", description="Final output of the model"
)

output_parser2 = StructuredOutputParser.from_response_schemas([response_schema3])

format_instructions2 = output_parser2.get_format_instructions()

llm = ChatGoogleGenerativeAI(
    google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-pro"
)


def get_name_info(food_name: TextIn):
    prompt_name = """
    for the given food_name please verify if it is an cooked food, raw food or not a food \
    and return food_type and ingredients \ 
    use the following instructions:

    INSTRUCTIONS:
    
    1. Food types :- Cooked food, Raw food, Not a food
    2. If it is a cooked food give me possible ingredients used in the food.
    3. if it is a raw food :- return Raw food, None
    4. if it is not a food t:- return not a food, None

    ``{food_name}```

    ```{format_instructions3}```
    """

    try:
        prompt = PromptTemplate(
            template=prompt_name,
            input_variables=["food_name"],
            partial_variables={"format_instructions3": format_instructions3},
        )

        chain = prompt | llm
        result = chain.invoke({"food_name": food_name})
        content = result.content.strip("```json\n").strip("\n```")
        result_dict = json.loads(content)
        response = NameResponse(
            name=food_name,
            type=result_dict["food_type"],
            ingredients=result_dict["ingredients"],
        )
        return response
    except Exception as e:
        print(f"An error occurred: {e}")


def get_nutrients(food_data: NameResponse):
    prompt_nutrients = """
    You are an expert Nutritionists, i will provide you with food_name or food_name + ingredients, provide me total \
    amount of nutrients present in the food found.

    NUTRIENTS:
    1.proteins
    2.fats 
    3.carbohydrates 
    4.vitamins 
    5.minerals
    ```{food_name}```
    ```{ingredients}```

    {format_instructions}
  """

    food_name = food_data.name
    ingredients = food_data.ingredients if food_data.ingredients else ""

    try:
        prompt = PromptTemplate(
            template=prompt_nutrients,
            input_variables=["food_name", "ingredients"],
            partial_variables={"format_instructions": format_instructions},
        )

        chain = prompt | llm
        output = chain.invoke({"food_name": food_name, "ingredients": ingredients})
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


def get_summary(nutrients: Nutrients):
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
    is_foodname = get_name_info(food_name)

    food_data = NameResponse(
        name=is_foodname.name,
        type=is_foodname.type,
        ingredients=is_foodname.ingredients,
    )

    if food_data.type != "not a food":
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
        return body, sentence
    else:
        print("The given input is not a Food")


if __name__ == "__main__":
    res = get_extracted_details("KFC Burger")
    print(res)
