import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import os
from dotenv import load_dotenv
import openai
import json
import random


def get_fake_column(name, type):
    '''
    Returns a fake column distrbution if it is int or float
    Or returns a list of fake column options if it is a string
    Query the OpenAI API for fake data, for this
    '''
    if type == int or type == float:
        message = f"Give me the distribution of data for column {name} of type {type} that I would expect in a dataset, \
        your response should be in the format of min and max number, just the 2 numbers of the type included on two different lines"
    elif type == bool:
         return [0, 1]
    else:
        message = f"Give me the list of 100 potential values for column named {name} of type {type} that I would expect in a dataset \
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


def get_col_distributions(tableCols):
    '''
    Returns the list of functions that return a random value for the given column distribution
    '''
    all_fake_columns = [get_fake_column(col.name, col.type) for col in tableCols]

    for col in tableCols:
        if col.type == int or col.type == float:
            col.fake_data = lambda: random.uniform(col.type[0], col.type[1])
        elif col.type == bool:
            col.fake_data = lambda: random.choice([0, 1])
        else:
            col.fake_data = lambda: random.choice(col.type)

    return [get_fake_column(col.name, col.type) for col in tableCols]

def get_fake_row(tableCols):
    '''
    Returns a fake row for the given table columns
    Query the OpenAI API for fake data, for this
    '''
    pass

load_dotenv()

# Testing fake columns
print(get_fake_column("age", int))

# Testing fake column distributions
print(get_fake_column("name", str))