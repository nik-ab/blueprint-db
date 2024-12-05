from enum import Enum
import pandas as pd
import dataset
import similarity_fasttext

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

    def find_column_matches(self, dataset, used_indexes):
        column_matches = []
        for column in self.columns:
            idx, _, _ = similarity_fasttext.get_best_match_idx(column.name, dataset.df.columns, used_indexes)
            used_indexes.append(idx)
            column_matches.append((dataset.name, idx))
            
            print(f"Matched {column.name} to {dataset.df.columns[idx]}")

        return column_matches

    def fit_to_dataset(self, dataset, used_indexes = None):
        if used_indexes is None:
            used_indexes = []

        column_matches = self.find_column_matches(dataset, used_indexes)

        df = pd.DataFrame()
        for column, (df_name, match_idx) in zip(self.columns, column_matches):
            df[column.name] = dataset.df[dataset.df.columns[match_idx]]
        
        df[self.name + "_id"] = range(len(df))

        return (df, column_matches)

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

class ERDiagram:
    def __init__(self, tables, relationships):
        self.tables = tables
        self.relationships = relationships

        for relationship in relationships:
            if relationship.from_table not in tables or relationship.to_table not in tables:
                raise ValueError("Invalid relationship")

    def __str__(self):
        res = "ER DIAGRAM\n"
        res += "\tTables:\n\t\t"
        res += "\n\t\t".join([str(table) for table in self.tables])
        res += "\n\tRelationships:\n\t\t"
        res += "\n\t\t".join([str(relationship) for relationship in self.relationships])
        return res

    def fit_to_dataset(self, dataset):
        res = []
        
        used_indexes = []
        for table in self.tables:
            df, matches = table.fit_to_dataset(dataset, used_indexes)
            print(matches)
            res.append((table, df))

        for relationship in self.relationships:
            if relationship.type != RelationshipType.ONE_TO_ONE:
                raise NotImplementedError("Only one-to-one relationships are supported")

            df = pd.DataFrame()
            df[relationship.from_table.name + "_id"] = range(len(dataset.df))
            df[relationship.to_table.name + "_id"] = range(len(dataset.df))

            res.append((relationship, df)) 

        return res


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

    diagram = ERDiagram(
        tables = [table1, table2],
        relationships = [
            Relationship("relationship_1", table1, table2, RelationshipType.ONE_TO_ONE)
        ]
    )

    dfs = diagram.fit_to_dataset(dataset)

    for table, df in dfs:
        print(table)
        df.to_csv(f"datasets/{table.name}.csv", index=False)
        print()
