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
    def __init__(self, name, columns, primary_key=None):
        self.name = name
        self.columns = columns

        if primary_key is not None and primary_key not in columns:
            raise ValueError("Primary key must be a column in the table")
        if primary_key is None:
            primary_key = Column("id", AttributeType.INTEGER)
            self.columns.append(primary_key)            

        self.primary_key = primary_key

    def __eq__(self, other):
        return self.name == other.name
    
    def __str__(self):
        return f"{self.name} [{', '.join([str(column) for column in self.columns])}], pk: {self.primary_key.name}"

    def fit_to_dataset(self, dataset):
        self.column_matches = []
        for column in self.columns:
            idx, _, _ = similarity_fasttext.get_best_match_idx(column.name, dataset.df.columns)
            self.column_matches.append((dataset.name, dataset.df.columns[idx]))


class RelationshipType(Enum):
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_ONE = 3
    MANY_TO_MANY = 4

class Relationship:
    def __init__(self, name, from_table, to_table, type, columns=None):
        self.name = name

        self.from_table = from_table
        self.to_table = to_table

        self.type = type

        self.columns = columns if columns is not None else []

    def __str__(self):
        return f"{self.name} ({self.from_table.name} to {self.to_table.name}, {self.type.name}) [{', '.join([str(column) for column in self.columns])}]"

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

if __name__ == "__main__":
    animal = Table(
        name = "animal",
        columns = [
            Column("name", AttributeType.STRING),
            Column("age", AttributeType.INTEGER)
        ]
    )
    adopter = Table(
        name = "adopter",
        columns = [
            Column("name", AttributeType.STRING),
            Column("phone", AttributeType.STRING),
            Column("email", AttributeType.STRING)
        ]
    )

    diagram = ERDiagram(
        tables = [animal, adopter],
        relationships = [
            Relationship(
                name = "adoption",
                from_table = animal,
                to_table = adopter,
                type = RelationshipType.MANY_TO_ONE,
                columns = [Column("adoption_date", AttributeType.DATE)]
            )
        ]
    )
    print(diagram)


    dataset1 = dataset.load_dataset("dataset1", "datasets/data.csv")
    table_to_fit = Table(
        name = "table_to_fit",
        columns = [
            Column("power", AttributeType.INTEGER),
            Column("popularity", AttributeType.INTEGER),
            Column("time", AttributeType.INTEGER)
        ]
    )
    table_to_fit.fit_to_dataset(dataset1)
    print(table_to_fit)
    print(table_to_fit.column_matches)