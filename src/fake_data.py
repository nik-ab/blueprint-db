import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import os
from dotenv import load_dotenv
import openai
import json
import random


def get_fake_column_dist(name):
    '''
    Returns a fake column distrbution if it is int or float
    Or returns a list of fake column options if it is a string
    Query the OpenAI API for fake data, for this
    '''
    # if type == int or type == float:
    #     message = f"Give me the possible distribution of data for column {name} of type {type} that I would expect in a dataset, \
    #     your response should be in the format of min and max number, \
    #     just the 2 numbers of the type included on two different lines \
    #     example output: 0.0 \n 100.0"
    # elif type == bool:
    #      return [0, 1]
    # else:
    message = f"Give me the list of 100 potential values for column named '{name}' that I would expect in a dataset \
    your response should be in the format of just the values (without enumeration) on different lines"

     # Set OpenAI API key
    openai.api_key = os.getenv("GPT_KEY")

    # Use the Chat API with 'messages' parameter
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message}
        ],
        max_tokens=100
    )

    # Extract and clean the response text
    keywords = response.choices[0].message['content'].strip().split("\n")
    return keywords

def get_fake_col(col_name, num_rows=10):
    '''
    Returns a fake row for the given table columns
    Query the OpenAI API for fake data, for this
    '''
    dist = get_fake_column_dist(col_name)
    return [
        random.choice(dist) for i in range(num_rows)
    ]


# load_dotenv()
# print(get_fake_rows([{"name": "age", "type": int}, {"name": "name", "type": str}, {"name": "is_student", "type": bool},
#                      {"name": "gpa", "type": float}, {"name": "major", "type": str}]))