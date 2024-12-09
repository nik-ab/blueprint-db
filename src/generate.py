import er_diagram
import scrape_kaggle
from dataset import load_dataset
import os
import fake_data


def generate_data(er_diagram):

    print("Generating data corresponding to the ER Diagram")
    print(er_diagram)

    os.makedirs(f"../gen/{er_diagram.name}", exist_ok=True)

    dfs = []

    for table in er_diagram.tables:
        print("Scraping Kaggle for table: ", table)

        dataset_name = scrape_kaggle.getDataset(
            table.name,
            ", ".join([column.name for column in table.columns])
        )

        print("Dataset found: ", dataset_name)
        dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}.csv")

        print(f"Fitting table {table.name} to dataset")
        unmatched = table.fit_to_dataset(dataset)

        print("Matched ones: ", table.df.columns)

        for col_name in unmatched:
            print(f"Generating fake data for column {col_name}")
            data = fake_data.get_fake_col(
                table.name + "." + col_name, len(dataset.df))
            table.df[col_name] = data

        dfs.append(table)
        table.df.to_csv(
            f"../gen/{er_diagram.name}/{table.name}.csv", index=False)
    return dfs


# def generate_data_alternate(er_diagram):

#     print("Generating data corresponding to the ER Diagram")
#     print(er_diagram)

#     os.makedirs(f"../gen/{er_diagram.name}", exist_ok=True)


#     columns = ""
#     for table in er_diagram.tables:
#         columns += ", ".join([f"{table.name}.{column.name}" for column in table.columns])

#     dataset_name = scrape_kaggle.getDataset(
#         er_diagram.name,
#         columns
#     )

#     print("Dataset found: ", dataset_name)
#     dataset = load_dataset(dataset_name, f"../datasets/{dataset_name}.csv")

#     res = er_diagram.fit_to_dataset(dataset)
#     for table, df in res:
#         df.to_csv(f"../gen/{er_diagram.name}/{table.name}.csv", index=False)


if __name__ == "__main__":
    table1 = er_diagram.Table(
        name="city",
        columns=[
            er_diagram.Column("name", er_diagram.AttributeType.STRING),
            er_diagram.Column(
                "average rent", er_diagram.AttributeType.INTEGER),
        ]
    )
    table2 = er_diagram.Table(
        name="vacations",
        columns=[
            er_diagram.Column("location", er_diagram.AttributeType.STRING),
            er_diagram.Column("price", er_diagram.AttributeType.INTEGER),
        ]
    )

    diag1 = er_diagram.ERDiagram(
        "diag1",
        tables=[table1],
        relationships=[]
    )

    generate_data(diag1)
