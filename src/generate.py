import er_diagram
import scrape_kaggle
from dataset import load_dataset

def generate_data(er_diagram):

    print("Generating data corresponding to the ER Diagram")
    print(er_diagram)

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

        df.to_csv(f"../gen/{table.name}.csv", index=False)




if __name__ == "__main__":
    Table1 = er_diagram.Table(
        name = "employees",
        columns = [
            er_diagram.Column("name", er_diagram.AttributeType.INTEGER),
            er_diagram.Column("age", er_diagram.AttributeType.INTEGER),
            ]
    )
    Table2 = er_diagram.Table(
        name = "pets",
        columns = [
            er_diagram.Column("name", er_diagram.AttributeType.INTEGER),
            er_diagram.Column("age", er_diagram.AttributeType.INTEGER),
            ]
    )

    er_diagram = er_diagram.ERDiagram(
        "employees",
        tables = [Table1, Table2],
        relationships = []
    )

    generate_data(er_diagram)




