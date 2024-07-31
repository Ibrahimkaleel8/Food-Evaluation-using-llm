PROMPT_NAME = """
    for the given food_name please verify if it is an cooked food, raw food or not a food \
    and return food_type and ingredients \ 
    use the following instructions:

    INSTRUCTIONS:
    
    1. Food types :- Cooked food, Raw food, Not a food
    2. If it is a cooked food give me possible ingredients used in the food.
    3. if it is a raw food :- return Raw food, None
    4. if it is not a food t:- return not a food, None
    ```{food_name}```

    ```{format_instructions3}```
"""


PROMPT_NUTRIENTS = """
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

    ```{format_instructions}```
"""

PROMPT_SUMMARY = """
    For the given nutrients of the specific food tell me how good is this for health \
    how frequently it can be consumed,and is there any bad impact on our health \
    the answer should not be more than 3 sentence, try to give answer in a creative sentence\
    ```{nutrients}```

    ```{format_instructions2}```
"""
