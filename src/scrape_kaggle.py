import kaggle
from kaggle.api.kaggle_api_extended import KaggleApi
import os
from dotenv import load_dotenv


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