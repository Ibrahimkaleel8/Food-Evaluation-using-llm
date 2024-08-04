import streamlit as st
import requests


st.title("Food Evaluation using Gemini 🍲")
st.subheader("")
st.subheader("Predicting the nutrients and details of food by providing its name")

api = "http://backend:3000/response"


def process(foodname: str, endpoint: str):
    payload = {"food_name": foodname}
    headers = {"Content-Type": "application/json"}
    r = requests.post(endpoint, json=payload, headers=headers)
    return r.json()


with st.form("my_form"):
    text_input = st.text_input("Enter name of the food 👇")
    submitted = st.form_submit_button("Submit")

    if submitted:
        res = process(text_input, api)

        if isinstance(res, list) and len(res) > 0:
            food_ingredients = res[0]
            food_info = res[1]
            response_text = ""
            if len(res) > 1 and isinstance(res[2], dict):
                response_text = res[1].get("response", "No response text available")
            st.subheader("Essential ingredients present in the food")
            st.write(f"{food_ingredients.get('ingredients','N/A')}")
            st.subheader("Nutrients presents")
            st.write(f"Name: {food_info.get('name', 'N/A')}")
            st.write(f"Proteins: {food_info.get('proteins', 'N/A')}")
            st.write(f"Fats: {food_info.get('fats', 'N/A')}")
            st.write(f"Carbohydrates: {food_info.get('carbohydrates', 'N/A')}")
            st.write(f"Vitamins: {food_info.get('vitamins', 'N/A')}")
            st.write(f"Minerals: {food_info.get('minerals', 'N/A')}")
            st.subheader("Summary")
            st.write(response_text)
        else:
            st.write("Given input is not a food")
