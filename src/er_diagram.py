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
        self.filled = False

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f"{self.name} [{', '.join([str(column) for column in self.columns])}]"

    def to_sql_schema(self, schema_name):
        res = "CREATE TABLE " + schema_name + "." + self.name + " (\n"
        res += "\t" + self.name + "_id INTEGER PRIMARY KEY,\n"
        res += "\t" + \
            ",\n\t".join(
                [column.name + " " + column.type.name for column in self.columns])
        res += "\n);"

        return res

    def gpt_query(self, dataset_columns):
        keywords = list(dataset_columns)

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
        query += "Columns: " + \
            ", ".join([column.name for column in self.columns]) + "\n"
        query += "Keywords: " + ", ".join(keywords) + "\n"

        res = gpt_wrapper.ask_gpt(query)

        print(query)
        print(res)

        return [pairs.split(", ") for pairs in res.split("\n")]

    def add_fake_data(self, column_name):
        print(f"Generating fake data for column {column_name}")
        data = fake_data.get_fake_col(
            self.name + "." + column_name, len(self.df))
        self.df[column_name] = data

    def fill_df(self, matches, dataset):
        self.df[self.name + "_id"] = range(len(dataset.df))

        for column_name, keyword_name in matches:
            if keyword_name == "UNMATCHED" or keyword_name not in dataset.df.columns:
                self.add_fake_data(column_name)
            else:
                dataset_column_idx = list(
                    dataset.df.columns).index(keyword_name)
                dataset_column = dataset.df[dataset.df.columns[dataset_column_idx]]
                self.df[column_name] = dataset_column

                print(f"Matched {column_name} to {keyword_name}")
                print(dataset_column)

        self.filled = True

    def fit_to_dataset(self, dataset):
        matches = self.gpt_query(dataset.df.columns)
        self.fill_df(matches, dataset)

        unused_columns = [column for column in dataset.df.columns if column not in [
            match[1] for match in matches]]
        return unused_columns

    def fit_to_dataset_if_good(self, dataset, unused_columns):
        matches = self.gpt_query(unused_columns)
        unmatched_cnt = len([x for x in matches if x[1] == "UNMATCHED"])
        match_ratio = (len(matches) - unmatched_cnt) / len(matches)
        if match_ratio < 0.5:
            return False, []
        self.fill_df(matches, dataset)
        unused_columns = [
            column for column in unused_columns if column not in [match[1] for match in matches]]

        return True, unused_columns


class RelationshipType(Enum):
    ONE_TO_ONE = 1
    ONE_TO_MANY = 2
    MANY_TO_ONE = 3
    MANY_TO_MANY = 4


class Relationship:
    def __init__(self, name, from_table, to_table, type, cols=[]):
        self.name = name

        self.from_table = from_table
        self.to_table = to_table

        self.type = type
        self.df = pd.DataFrame(
            columns=[self.from_table.name + "_id", self.to_table.name + "_id"] + cols)

    def __str__(self):
        return f"{self.name} ({self.from_table.name} to {self.to_table.name}, {self.type.name})"

    def to_sql_schema(self, schema_name):
        res = "CREATE TABLE " + schema_name + "." + self.name + " (\n"
        res += "\t" + self.from_table.name + "_id INTEGER UNIQUE,\n"
        res += "\t" + self.to_table.name + "_id INTEGER UNIQUE,\n"
        res += "\tPRIMARY KEY (" + self.from_table.name + \
            "_id, " + self.to_table.name + "_id),\n"
        res += "\tFOREIGN KEY (" + self.from_table.name + "_id) REFERENCES " + \
            self.from_table.name + "(" + self.from_table.name + "_id),\n"
        res += "\tFOREIGN KEY (" + self.to_table.name + "_id) REFERENCES " + \
            self.to_table.name + "(" + self.to_table.name + "_id)\n"
        res += ");"

        return res

    def fill_trivially(self, size):
        self.df[self.from_table.name + "_id"] = range(size)
        self.df[self.to_table.name + "_id"] = range(size)


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
        res += "\n\t\t".join([str(relationship)
                             for relationship in self.relationships])
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
            if table.filled:
                continue

            print(f"Generating data for table {table.name}")
            dataset_name = scrape_kaggle.getDataset(
                table.name, ", ".join([column.name for column in table.columns]))
            print("Dataset found: ", dataset_name)
            dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}")

            unused_columns = table.fit_to_dataset(dataset)

            for relation in self.relationships:
                if len(unused_columns) == 0:
                    break
                if relation.type != RelationshipType.ONE_TO_ONE:
                    continue
                other_table = relation.to_table if relation.from_table == table else relation.from_table
                if other_table.filled:
                    continue
                fill_res, new_unused = other_table.fit_to_dataset_if_good(
                    dataset, unused_columns)
                if not fill_res:
                    print(f"Failed to fit table {other_table.name} to dataset")
                    break
                print(f"Successfully fit table {other_table.name} to dataset")

                unused_columns = new_unused
                relation.fill_trivially(len(dataset.df))
                break

    def save_to_csv(self):
        if not os.path.exists(f"../gen/{self.name}"):
            os.makedirs(f"../gen/{self.name}")

        for table in self.tables:
            table.df.to_csv(
                f"../gen/{self.name}/{table.name}.csv", index=False)

        for relationship in self.relationships:
            relationship.df.to_csv(
                f"../gen/{self.name}/{relationship.name}.csv", index=False)


if __name__ == "__main__":
    table1 = Table(
        name="Country",
        columns=[
            Column("name", AttributeType.STRING),
            Column("population", AttributeType.INTEGER),
        ]
    )
    table2 = Table(
        name="Capital",
        columns=[
            Column("capital", AttributeType.STRING),
        ]
    )

    relationship1 = Relationship(
        name="CountryCapital",
        from_table=table1,
        to_table=table2,
        type=RelationshipType.ONE_TO_ONE
    )

    diag1 = ERDiagram(
        "diag1",
        tables=[table1, table2],
        relationships=[relationship1]
    )

    diag1.populate_with_data()
    diag1.save_to_csv()
