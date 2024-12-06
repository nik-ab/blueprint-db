from flask import Flask, request
from flask_cors import CORS
from er_diagram import *
import json
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8000"}})


def convertJSONToERDiagram(json):
    tables = []
    for table_json in json["tables"]:
        columns = []
        for column_json in table_json["columns"]:
            print(column_json["type"])
            columns.append(
                Column(column_json["name"], AttributeType(column_json["type"])))
        tables.append(Table(table_json["name"], columns))

    relationships = []
    for relationship in json["relationships"]:
        table_idxs = relationship["tables"]
        relationship_types_arr = relationship["relationshipType"]
        relationship_type = RelationshipType(
            relationship_types_arr[0] * 2 + relationship_types_arr[1] + 1)
        relationships.append(Relationship(
            relationship["name"], tables[table_idxs[0]], tables[table_idxs[1]], relationship_type))

    return ERDiagram('table', tables, relationships)


@app.route('/')
def hello():
    print('hello world')
    return 'Hello, World!'


@app.route('/generate', methods=['POST'])
def generate():
    er_diagram = request.get_json()
    print(er_diagram)
    converted = convertJSONToERDiagram(er_diagram)
    print(converted)

    # Assuming you have a sample database stored as a pandas DataFrame
    sample_database = pd.DataFrame({
        'Name': ['John', 'Jane', 'Mike'],
        'Age': [25, 30, 35],
        'City': ['New York', 'London', 'Paris']
    })

    return sample_database.to_json()


if __name__ == '__main__':
    app.run()
    app.run(port=5000)