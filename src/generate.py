import er_diagram
import scrape_kaggle
from dataset import load_dataset
import os

def generate_data(er_diagram):

    print("Generating data corresponding to the ER Diagram")
    print(er_diagram)

    os.makedirs(f"../gen/{er_diagram.name}", exist_ok=True)    

    for table in er_diagram.tables:
        print("Scraping Kaggle for table: ", table)

        dataset_name = scrape_kaggle.getDataset(
        table.name,
        ", ".join([column.name for column in table.columns])
        )

        print("Dataset found: ", dataset_name)
        dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}.csv")

        print(f"Fitting table {table.name} to dataset")
        df = table.fit_to_dataset(dataset)

        df.to_csv(f"../gen/{er_diagram.name}/{table.name}.csv", index=False)


def generate_data_alternate(er_diagram):

    print("Generating data corresponding to the ER Diagram")
    print(er_diagram)

    os.makedirs(f"../gen/{er_diagram.name}", exist_ok=True)    


    columns = ""
    for table in er_diagram.tables:
        columns += ", ".join([f"{table.name}.{column.name}" for column in table.columns])

    dataset_name = scrape_kaggle.getDataset(
        er_diagram.name,
        columns
    )

    print("Dataset found: ", dataset_name)
    dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}.csv")

    res = er_diagram.fit_to_dataset(dataset)
    for table, df in res:
        df.to_csv(f"../gen/{er_diagram.name}/{table.name}.csv", index=False)



if __name__ == "__main__":
    table1 = er_diagram.Table(
        name = "employees",
        columns = [
            er_diagram.Column("name", er_diagram.AttributeType.INTEGER),
            er_diagram.Column("age", er_diagram.AttributeType.INTEGER),
            ]
    )
    table2 = er_diagram.Table(
        name = "pets",
        columns = [
            er_diagram.Column("name", er_diagram.AttributeType.INTEGER),
            er_diagram.Column("age", er_diagram.AttributeType.INTEGER),
            ]
    )

    diag1 = er_diagram.ERDiagram(
        "diag1",
        tables = [table1, table2],
        relationships = []
    )

    generate_data(diag1)


    alt_table1 = er_diagram.Table(
        name = "employees",
        columns = [
            er_diagram.Column("name", er_diagram.AttributeType.INTEGER),
            er_diagram.Column("age", er_diagram.AttributeType.INTEGER),
            ]
    )
    alt_table2 = er_diagram.Table(
        name = "salaries",
        columns = [
            er_diagram.Column("amount", er_diagram.AttributeType.INTEGER),
            ]
    )

    relationships = [
        er_diagram.Relationship(
            "employees_salaries",
            alt_table1,
            alt_table2,
            er_diagram.RelationshipType.ONE_TO_ONE
        )
    ]

    diag2 = er_diagram.ERDiagram(
        "diag2",
        tables = [alt_table1, alt_table2],
        relationships = relationships
    )

    generate_data_alternate(diag2)





