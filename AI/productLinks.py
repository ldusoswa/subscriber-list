# a python script which connects to OpenAI API and retrieves prices and links for a given sim racing product from a set list of websites.
from openai import OpenAI
import re
import os

websites = [
    "fanatec.com",
    "simracecity.com",
    "trakracer.com",
]

role = "You are a chat bot that helps users find links to products. You will search a known list of websites for the product and return a correct link to the appropriate product page. This page must exist and be accessible to the user. You will ignore any websites which do not stock the product. You will return up to 3 results."

def get_openai_response(prompt, model="gpt-4o"):
    try:
        client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

        # Send the prompt to the OpenAI API and get the response
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": role},
                {"role": "user", "content": prompt},
            ]
        )

        text = response.choices[0].message.content.strip()
        return text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # prompt the user for a product name
    product_name = input("Enter the name of the product you want to search for: ")

    # Define the prompt you want to send to the OpenAI API
    prompt = f"Get links for the product {product_name} from the following websites: {', '.join(websites)}"

# Get the response from OpenAI
    response_text = get_openai_response(prompt)

    # Print the response
    print("OpenAI Response:")
    print(response_text)
