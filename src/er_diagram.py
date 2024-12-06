from enum import Enum
import pandas as pd
import dataset
import gpt_wrapper
# import similarity_fasttext

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

    def __eq__(self, other):
        return self.name == other.name
    
    def __str__(self):
        return f"{self.name} [{', '.join([str(column) for column in self.columns])}]"

    # def find_column_matches(self, dataset, used_indexes):
    #     column_matches = []
    #     for column in self.columns:
    #         idx, _, _ = similarity_fasttext.get_best_match_idx(column.name, dataset.df.columns, used_indexes)
    #         used_indexes.append(idx)
    #         column_matches.append((dataset.name, idx))
            
    #         print(f"Matched {column.name} to {dataset.df.columns[idx]}")

    #     return column_matches

    # def fit_to_dataset(self, dataset, used_indexes = None):
    #     if used_indexes is None:
    #         used_indexes = []

    #     column_matches = self.find_column_matches(dataset, used_indexes)

    #     df = pd.DataFrame()
    #     for column, (df_name, match_idx) in zip(self.columns, column_matches):
    #         df[column.name] = dataset.df[dataset.df.columns[match_idx]]
        
    #     df[self.name + "_id"] = range(len(df))

    #     return (df, column_matches)
    
    def to_sql_schema(self, schema_name):
        res = "CREATE TABLE " + schema_name + "." + self.name + " (\n"
        res += "\t" + self.name + "_id INTEGER PRIMARY KEY,\n"
        res += "\t" + ",\n\t".join([column.name + " " + column.type.name for column in self.columns])
        res += "\n);"

        return res

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
        query += "The names of the tables and its columns are provided in the following format (table_idx, table_name, column_idx_0, column_name_0,  column_idx_1, column_name_1, ...)\n"
        for i, table in enumerate(self.tables):
            query += f"({i}, {table.name}, {', '.join([f'{j}, {column.name}' for j, column in enumerate(table.columns)])})\n"
        
        query += "I want to match each column in each dataset to one of the keywords below\n"
        query += "The keywords are provided in the following format (keyword_idx, keyword_name)\n"
        query += "\n".join([f"({i}, {keyword})" for i, keyword in enumerate(dataset.df.columns)])

        query += "\nEach table column should be matched to exactly one keyword\n"
        query += "Each keyword should be matched to at most one table column\n"

        query += "Provide the answer in the following format (table_idx, table_column_idx, keyword_idx), where each tuple is on a new line\n"
        query += "I will be parsing your output, so please make sure it is in the correct format, and dont any extra text\n"
        query += "An example output would be:\n"
        query += "(0, 0, 0)\n(0, 1, 1)\n(1, 0, 2)\n(1, 1, 3)\n"

        res = gpt_wrapper.ask_gpt(query)
       
        triplets = res.split("\n")
        matches = []
        for triplet in triplets:
            table_idx, table_column_idx, keyword_idx = triplet.split(",")
            table_idx = table_idx.strip("(")
            keyword_idx = keyword_idx.strip(")")
            matches.append((int(table_idx), int(table_column_idx), int(keyword_idx)))
        
        return matches
        
    def fit_to_dataset_gpt(self, dataset):
        matches = self.gpt_query(dataset)
        
        dfs = [
            pd.DataFrame() for table in self.tables
        ]
        for df, table in zip(dfs, self.tables):
            df[table.name + "_id"] = range(len(dataset.df))
        

        for table_idx, table_column_idx, dataset_column_idx in matches:
            
            table_name = self.tables[table_idx].name
            column_name = self.tables[table_idx].columns[table_column_idx].name
            dataset_column_name = dataset.df.columns[dataset_column_idx]

            print(f"Matched {table_name}.{column_name} to {dataset_column_name}")

            df = dfs[table_idx]
            df[column_name] = dataset.df[dataset.df.columns[dataset_column_idx]]
        
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

    # def fit_to_dataset(self, dataset):
    #     res = []
        
    #     used_indexes = []
    #     for table in self.tables:
    #         df, matches = table.fit_to_dataset(dataset, used_indexes)
    #         print(matches)
    #         res.append((table, df))

    #     for relationship in self.relationships:
    #         if relationship.type != RelationshipType.ONE_TO_ONE:
    #             raise NotImplementedError("Only one-to-one relationships are supported")

    #         df = pd.DataFrame()
    #         df[relationship.from_table.name + "_id"] = range(len(dataset.df))
    #         df[relationship.to_table.name + "_id"] = range(len(dataset.df))

    #         res.append((relationship, df)) 

    #     return res


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
            Column("instruments", AttributeType.INTEGER),
        ]
    )

    diagram = ERDiagram( "hello_world",
        tables = [table1, table2],
        relationships = [
            Relationship("relationship_1", table1, table2, RelationshipType.ONE_TO_ONE)
        ]
    )

    print(diagram.to_sql_schema())

    dfs = diagram.fit_to_dataset_gpt(dataset)
    for table, df in dfs:
        print(table)
        df.to_csv(f"datasets/{table.name}.csv", index=False)
        print()