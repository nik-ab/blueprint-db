from enum import Enum

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

class Table:
    def __init__(self, name, columns):
        self.name = name
        self.columns = columns
    
    def __eq__(self, other):
        return self.name == other.name

class RelationshipType(Enum):
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_ONE = 3
    MANY_TO_MANY = 4

class Relationship:
    def __init__(self, name, from_table, to_table, from_exact, to_exact, type):
        self.name = name

        self.from_table = from_table
        self.from_exact = from_exact

        self.to_table = to_table
        self.to_exact = to_exact

        self.type = type


class ERDiagram:
    def __init__(self, tables, relationships):
        self.tables = tables
        self.relationships = relationships

        for relationship in relationships:
            if relationship.from_table not in tables or relationship.to_table not in tables:
                raise ValueError("Invalid relationship")


if __name__ == "__main__":
    animal = Table(
        name = "animal",
        columns = [
            Column("id", AttributeType.INTEGER),
            Column("name", AttributeType.STRING),
            Column("age", AttributeType.INTEGER)
        ]
    )
    adopter = Table(
        name = "adopter",
        columns = [
            Column("id", AttributeType.INTEGER),
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
                from_exact = False,
                to_table = adopter,
                to_exact = False,
                type = RelationshipType.MANY_TO_ONE
            )
        ]
    )