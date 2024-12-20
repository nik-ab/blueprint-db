# Blueprint DB

Final Project for 6.5830/6.5831

Team Members
Nikoloz Birkadze — birka@mit.edu

Ege Kabasakaloglu — egekabas@mit.edu

Tamar Korkotashvili — tkorkot@mit.edu

# Abstract

The project aims to automate the process of populating Entity-Relationship (ER) schemas by leveraging online data sources. By utilizing Google’s data search API and other web scraping techniques, our system will dynamically fill in the necessary attributes based on predefined relational schemas. The "big idea" is to enhance the efficiency and accuracy of database schema development, thereby reducing manual data entry and improving data quality.

This project addresses the need of creating large test datasets for provided database schemas in user applications. In case of unavailability of online public datasets, we aim to create fake, testing data, taking into consideration all the edge cases of the relations, for the users to test their application or their queries.

# How to run

**Python dependencies:** pandas, kaggle, openai, dotenv, json, matplotlib, shutil, flask, flask_cors, fasttext.util, numpy, gensim.models

OpenAI packages might need migration to a older version, in that case we recommend migrating to version 0.28 as proposed to the Error message.

**Setting up .env:** To access the openai and kaggle APIs, a .env file needs to be created at the root of the directory with the following variables: GPT_KEY, KAGGLE_USERNAME, KAGGLE_KEY, corresponding to valid keys and usernames for the respective services.

**Running the server:** Navigate to the src folder and run `python server.py`
**Running the front end:** Navigate to the client folder and run `python -m http.server`

[Project Paper](BlueprintDB.pdf)
