import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import os
from dotenv import load_dotenv
import openai


def gptTableKeywords(tabelName, tableCols):
    keyword_string = ("Give me short search keywords that I can use to search for dataset " + tabelName
                      + " in Kaggle. The table has the following columns: " + tableCols + "."
                      + " Give me 5 different options to search for this dataset.")
    
    # Query the GPT-3 model for the keywords
    openai.api_key = os.getenv("GPT_KEY")
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        prompt = keyword_string,
        max_tokens = 100
    )

    # Filter the response to get the keywords
    keywords = response.choices[0].text.split("\n")[1:-1]
    return keywords

def getDatasetNames(keywords):
    # Query the Kaggle API for datasets with the given keywords
    datasets = set()

    for keyword in keywords:
        for dataset in api.dataset_list(search=keyword):
            datasets.add([dataset.ref, dataset.title])
    
    return datasets

def chooseBestDataset(datasets, tableCols):
    # Download the datasets with the ref from kaggle
    for dataset in datasets:
        api.dataset_download_files(dataset[0], path="datasets/", force=True)
        with open("datasets/" + dataset[1] + ".zip", "r") as f:
            # Unzip the file and save column names
            pass

    # Run the column matching algorithm and get the matching scores

    # Delete all the other datasets
    return best_dataset


# Loading environment variables
load_dotenv()

# Set up Kaggle environment variables directly in Python
os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")

# Logging in to Kaggle
api = KaggleApi()
api.authenticate()

datasets = api.dataset_list(search="boston weather")

for dataset in datasets:
    print (dataset)
    print(f"Title: {dataset.title}")
    print(f"Description: {dataset.description}\n")


gptTableKeywords("boston weather", "date, temperature, precipitation, wind_speed, humidity")