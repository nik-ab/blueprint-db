import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import os
from dotenv import load_dotenv
import openai
import json

# Loading environment variables
load_dotenv()

# Set up Kaggle environment variables directly in Python
os.environ["KAGGLE_USERNAME"] = os.getenv("KAGGLE_USERNAME")
os.environ["KAGGLE_KEY"] = os.getenv("KAGGLE_KEY")
os.environ["GPT_KEY"] = os.getenv("GPT_KEY")

# Get Kaggle username and key from environment variables
kaggle_username = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

if not kaggle_username or not kaggle_key:
    raise ValueError("Kaggle username or key is missing. Check your .env file.")

# Create the content for kaggle.json
kaggle_config = {
    "username": kaggle_username,
    "key": kaggle_key
}

# Define the path for kaggle.json
kaggle_dir = os.path.expanduser("~/.kaggle")
kaggle_json_path = os.path.join(kaggle_dir, "kaggle.json")

# Ensure the ~/.kaggle directory exists
os.makedirs(kaggle_dir, exist_ok=True)

# Write kaggle.json
with open(kaggle_json_path, "w") as f:
    json.dump(kaggle_config, f)

# Set the correct permissions for the file
os.chmod(kaggle_json_path, 0o600)

print(f"kaggle.json created successfully at {kaggle_json_path}")

def gptTableKeywords(tableName, tableCols):
    keyword_string = (f"Give me short search keywords that I can use to search for a dataset called '{tableName}'. "
                      f"The table has the following columns: {tableCols}. "
                      "Give me 5 different options to search for this dataset."
                      f"in the format of new keywords as a single string on a new line. ")
    
    # Set OpenAI API key
    openai.api_key = os.getenv("GPT_KEY")

    # Use the Chat API with 'messages' parameter
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": keyword_string}
        ],
        max_tokens=100
    )

    # Extract and clean the response text
    keywords = response.choices[0].message['content'].strip().split("\n")
    return keywords

def getDatasetNames(keywords):
    # Query the Kaggle API for datasets with the given keywords
    datasets = set()

    # Logging in to Kaggle
    api = KaggleApi()
    api.authenticate()

    for keyword in keywords:
        all_datasets = api.dataset_list(search=keyword)
        for dataset in all_datasets:
            datasets.add((dataset.ref, dataset.title))
    #print(datasets)
    return datasets

def chooseBestDataset(datasets, tableCols):
    # Ask chatgpt which dataset is the best
    dataset_string = (f"I have found {len(datasets)} datasets that might be relevant. "
                      "Help me choose the best dataset that probably is the most similar with the title."
                      "From the list of datasets that I provide below, give me the whole line entry of the  dataset that you think is the best matching/appropriate. " 
                      "Here are the titles of the datasets and tags for downloading those: \n")
    
    for dataset in datasets:
        dataset_string = dataset_string + dataset[1] + "&" + dataset[0] + "\n"
    
    dataset_string += "Please choose the best dataset for the given table columns: "
    dataset_string += str(tableCols)

    print(dataset_string)

    # Set OpenAI API key
    openai.api_key = os.getenv("GPT_KEY")

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": dataset_string}
        ],
        max_tokens=100
    )

    # Extract and clean the response text
    best_dataset = response.choices[0].message['content'].strip()
    
    # Extract the dataset tag from the response
    best_dataset_name = best_dataset.split("&")[0]
    best_dataset_tag = best_dataset.split("&")[-1]


    print(best_dataset_tag, best_dataset_name)

    # Download the dataset
    #api.dataset_download(best_dataset_tag, path="../datasets/")
    # Logging in to Kaggle
    # api = KaggleApi()
    # api.authenticate()
    # download_path = "../datasets/"
    # api.dataset_download_files(best_dataset_tag, path=download_path, unzip=True)
    #api.dataset_download_files(best_dataset_tag, path="../datasets/", unzip=True)
    return best_dataset_name


keywords = gptTableKeywords("boston weather", "date, temperature, precipitation, wind_speed, humidity")
datasets = getDatasetNames(keywords)
best_dataset = chooseBestDataset(datasets, "date, temperature, precipitation, wind_speed, humidity")
print(best_dataset)

# Download the dataset
# api = KaggleApi()
# api.authenticate()
# api.dataset_download_files(dataset, path=download_path, unzip=True)