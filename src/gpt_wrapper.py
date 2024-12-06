import openai
import os
from dotenv import load_dotenv

load_dotenv()

def ask_gpt(query):
    openai.api_key = os.getenv("GPT_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": query}
        ],
        max_tokens=100
    )
    return response.choices[0].message['content'].strip()


