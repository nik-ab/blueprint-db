from enum import Enum
import pandas as pd
from dataset import load_dataset
import gpt_wrapper
import os
import scrape_kaggle
import fake_data

class AttributeType(Enum):
    STRING = 1
    INTEGER = 2
    FLOAT = 3
    BOOLEAN = 4
    DATE = 5
    TIME = 6
    DATETIME = 7
    BINARY = 8


class Column:
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f"{self.name} ({self.type.name})"

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
        self.df = pd.DataFrame()

    def __eq__(self, other):
        return self.name == other.name
    
    def __str__(self):
        return f"{self.name} [{', '.join([str(column) for column in self.columns])}]"
    
    def to_sql_schema(self, schema_name):
        res = "CREATE TABLE " + schema_name + "." + self.name + " (\n"
        res += "\t" + self.name + "_id INTEGER PRIMARY KEY,\n"
        res += "\t" + ",\n\t".join([column.name + " " + column.type.name for column in self.columns])
        res += "\n);"

        return res
    

    def gpt_query(self, dataset):
        keywords = list(dataset.df.columns)
        
        query = "Match the names in the columns to the keywords\n"
        query += "Give the answer in the following format 'column_name, keyword_name', where each tuple is on a new line\n"
        query += "If you don't think a good match exists, you can leave the column unmatched by providing the tuple 'column_name, UNMATCHED'\n"
        query += "Please dont add any extra text, as I will be parsing your output\n"
        query += "Moreover, each keyword should be matched to at most one column\n"
        query += "An example input would be:\n"
        query += "Columns: name, profession, location, hobby\n"
        query += "Keywords: name, city, job, parents, siblings\n"
        query += "An example output to this input would be:\n"
        query += "name, name\nprofession, job\nlocation, city\nhobby, UNMATCHED\n"
        query += "Here, hobby was left unmatched as there was no good match\n"
        query += "It is EXTREMELY important that you leave columns unmatched if you think no good match exists\n"
        query += "Now I will provide you with the input you should respond to\n"
        query += "Columns: " + ", ".join([column.name for column in self.columns]) + "\n"
        query += "Keywords: " + ", ".join(keywords) + "\n"

        print("Querying GPT-3 with the following prompt:")
        print(query)

        res = gpt_wrapper.ask_gpt(query)
        print("GPT-3 response:")
        print(res)

        return [pairs.split(", ") for pairs in res.split("\n")]

    def fit_to_dataset(self, dataset):
        matches = self.gpt_query(dataset)
        
        self.df[self.name + "_id"] = range(len(dataset.df))

        unmatched = []

        for column_name, keyword_name in matches:
            if keyword_name == "UNMATCHED":
                print(f"Column {column_name} was left unmatched")
                unmatched.append(column_name)
                continue

            dataset_column_idx = list(dataset.df.columns).index(keyword_name)
            dataset_column = dataset.df[dataset.df.columns[dataset_column_idx]]
            self.df[column_name] = dataset_column  
            
            print(f"Matched {column_name} to {keyword_name}")
            print(dataset_column)



        for col_name in unmatched:
            print(f"Generating fake data for column {col_name}")
            data = fake_data.get_fake_col(self.name + "." + col_name, len(dataset.df))
            self.df[col_name] = data

class RelationshipType(Enum):
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_ONE = 3
    MANY_TO_MANY = 4

class Relationship:
    def __init__(self, name, from_table, to_table, type, cols = []):
        self.name = name

        self.from_table = from_table
        self.to_table = to_table

        self.type = type
        columns = ['id_0', 'id_1'] + cols
        self.df = pd.DataFrame(columns=columns)

    def __str__(self):
        return f"{self.name} ({self.from_table.name} to {self.to_table.name}, {self.type.name})"
    
    def to_sql_schema(self, schema_name):
        res = "CREATE TABLE " + schema_name + "." + self.name + " (\n"
        res += "\t" + self.from_table.name + "_id INTEGER UNIQUE,\n"
        res += "\t" + self.to_table.name + "_id INTEGER UNIQUE,\n"
        res += "\tPRIMARY KEY (" + self.from_table.name + "_id, " + self.to_table.name + "_id),\n"
        res += "\tFOREIGN KEY (" + self.from_table.name + "_id) REFERENCES " + self.from_table.name + "(" + self.from_table.name + "_id),\n"
        res += "\tFOREIGN KEY (" + self.to_table.name + "_id) REFERENCES " + self.to_table.name + "(" + self.to_table.name + "_id)\n"
        res += ");"

        return res

class ERDiagram:
    def __init__(self, name, tables, relationships):
        self.name = name
        self.tables = tables
        self.relationships = relationships

        for relationship in relationships:
            if relationship.from_table not in tables or relationship.to_table not in tables:
                raise ValueError("Invalid relationship")

    def __str__(self):
        res = "ER DIAGRAM " + self.name + "\n"
        res += "\tTables:\n\t\t"
        res += "\n\t\t".join([str(table) for table in self.tables])
        res += "\n\tRelationships:\n\t\t"
        res += "\n\t\t".join([str(relationship) for relationship in self.relationships])
        return res


    def to_sql_schema(self):
        res = "CREATE SCHEMA " + self.name + ";\n\n"

        for table in self.tables:
            res += table.to_sql_schema(self.name) + "\n\n"

        for relationship in self.relationships:
            res += relationship.to_sql_schema(self.name) + "\n\n"

        return res


    def populate_with_data(self):
        for table in self.tables:
            print(f"Generating data for table {table.name}")
            dataset_name = scrape_kaggle.getDataset(table.name, ", ".join([column.name for column in table.columns]))
            print("Dataset found: ", dataset_name)
            dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}.csv")
            
            print(f"Fitting table {table.name} to dataset")
            table.fit_to_dataset(dataset)


    def save_to_csv(self):
        if not os.path.exists(f"../gen/{self.name}"):
            os.makedirs(f"../gen/{self.name}")

        for table in self.tables:
            table.df.to_csv(f"../gen/{self.name}/{table.name}.csv", index=False)

if __name__ == "__main__":
    table1 = Table(
        name = "city",
        columns = [
            Column("name", AttributeType.STRING),
            Column("population", AttributeType.INTEGER),
            ]
    )
    table2 = Table(
        name = "country",
        columns = [
            Column("location", AttributeType.STRING),
            Column("name", AttributeType.INTEGER),
            ]
    )

    diag1 = ERDiagram(
        "diag1",
        tables = [table1],
        relationships = []
    )

    diag1.populate_with_data()
    diag1.save_to_csv()