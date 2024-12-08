from enum import Enum
import pandas as pd
import dataset
import gpt_wrapper
import os

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
        # query = "I have a table in a relational schema and it has a bunch of columns\n"
        # query += "I want to match each column in the table to some keywords\n"
        # query += "You should give the answer in the following format 'column_name, keyword_name', where each tuple is on a new line\n"
        # query += "If you don't think a good match exists, you can leave the column unmatched\n"
        # query += "Please dont add any extra text, as I will be parsing your output\n"
        # query += "Moreover, each keyword should be matched to at most one column\n"
        # query += "An example input would be:\n"
        # query += "Columns: name, profession, location, hobby\n"
        # query += "Keywords: name, city, job, parents, siblings\n"
        # query += "An example output to this input would be:\n"
        # query += "name, name\nprofession, job\nlocation, city\n"
        # query += "Here, hobby was left unmatched as there was no good match\n"
        # query += "It is EXTREMELY important that you leave columns unmatched if you think no good match exists\n"
        # query += "Now I will provide you with the input you should respond to\n"
        # query += "Columns: " + ", ".join([column.name for column in self.columns]) + "\n"
        # query += "Keywords: " + ", ".join(keywords) + "\n"
        
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
        
        return unmatched

class RelationshipType(Enum):
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_ONE = 3
    MANY_TO_MANY = 4

class Relationship:
    def __init__(self, name, from_table, to_table, type):
        self.name = name

        self.from_table = from_table
        self.to_table = to_table

        self.type = type

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


    def gpt_query(self, dataset):
        query = "I have a bunch of table in a relational schema and each table has a bunch of columns\n"
        query += "The names of the tables and its columns are provided in the following format (table_name, column_name_0, column_name_1, ...)\n"
        for i, table in enumerate(self.tables):
            query += f"({table.name}, {', '.join(column.name for column in table.columns)})\n"
        
        query += "I want to match each column in each dataset to one of the keywords below\n"
        query += "\n".join(dataset.df.columns)

        query += "\nEach table column should be matched to at most one keyword\n"
        query += "Each keyword should be matched to at most one table column\n"
        query += "You can leave a table unmatched if you think no good match exists\n"

        query += "Provide the answer in the following format (table_name, column_name, keyword_name), where each tuple is on a new line\n"
        query += "I will be parsing your output, so please make sure it is in the correct format, and dont any extra text\n"
        query += "An example input would be:\n"
        query += "(dogs, name, weight)\n(cats, name, type, age)\n"
        query += "dog_name, cat_name, kilos, species\n"
        query += "An example output to this input would be:\n"
        query += "(dogs, name, dog_name)\n(dogs, weight, kilos)\n(cats, name, cat_name)\n(cats, type, species)\n"
        query += "Notice how I left cats.age unmatched, as there was no good match\n"

        print(query)

        res = gpt_wrapper.ask_gpt(query)
       
        print(res)

        triplets = res.split("\n")
        matches = [
            [name.strip("() ") for name in triplet.split(",")] for triplet in triplets 
        ]
        print(matches)
        
        return matches
        
    def fit_to_dataset(self, dataset):
        matches = self.gpt_query(dataset)
        
        dfs = [
            pd.DataFrame() for table in self.tables
        ]
        for df, table in zip(dfs, self.tables):
            df[table.name + "_id"] = range(len(dataset.df))
        

        for table_name, column_name, keyword_name in matches:
            table_idx = [table.name for table in self.tables].index(table_name)
            table_column_idx = [column.name for column in self.tables[table_idx].columns].index(column_name)
            dataset_column_idx = list(dataset.df.columns).index(keyword_name)
            
            print(f"Matched {table_name}.{column_name} to {keyword_name}")

            df = dfs[table_idx]
            df[column_name] = dataset.df[dataset.df.columns[dataset_column_idx]]
        
        for table in self.tables:
            for column in table.columns:
                if column.name not in df.columns:
                    print(f"Column {column.name} in table {table.name} was not matched")
        
        for relationship in self.relationships:
            if relationship.type != RelationshipType.ONE_TO_ONE:
                raise NotImplementedError("Only one-to-one relationships are supported")

            df = pd.DataFrame()
            df[relationship.from_table.name + "_id"] = range(len(dataset.df))
            df[relationship.to_table.name + "_id"] = range(len(dataset.df))

            dfs.append(df)

        return [
            (table, df) for table, df in zip(self.tables, dfs)
        ] + [
            (relationship, df) for relationship, df in zip(self.relationships, dfs[len(self.tables):])
        ]



if __name__ == "__main__":
    dataset = dataset.load_dataset("dataset1", "datasets/data.csv")
    
    table1 = Table(
        name = "table_1",
        columns = [
            Column("power", AttributeType.INTEGER),
            Column("popular", AttributeType.INTEGER),
            Column("time", AttributeType.INTEGER)
        ]
    )

    table2 = Table(
        name = "table_2",
        columns = [
            Column("acoustics", AttributeType.INTEGER),
            Column("dont_match_this_to_anything_plaeas", AttributeType.INTEGER),
        ]
    )

    diagram = ERDiagram( "hello_world",
        tables = [table1, table2],
        relationships = [
            Relationship("relationship_1", table1, table2, RelationshipType.ONE_TO_ONE)
        ]
    )

    print(diagram.to_sql_schema())

    dfs = diagram.fit_to_dataset(dataset)
    for table, df in dfs:
        if os.path.exists("gen") == False:
            os.mkdir("gen")
        df.to_csv(f"gen/{table.name}.csv", index=False)
        print()