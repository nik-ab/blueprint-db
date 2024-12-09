import pandas as pd
from src.dataset import Diagram, Table, Relationship, RelationshipType
import random
from src.fake_data import get_fake_row


def check_one(relationship, direction):
    '''
    df is the table that represents the relationship between the two tables
    it has id_0, id_1, representing the rows in the subsequent from_table and to_table 
    other columns 
    '''

    # Get the from table and to table
    from_df = relationship.from_table.df
    to_df = relationship.to_table.df

    no_from_ids = len(from_df)
    no_to_ids = len(to_df)

    # create a set with no_from_ids 0 to no_from_ids - 1
    # create a set with no_to_ids 0 to to_from_ids - 1
    from_set = set([i for i in range(no_from_ids)])
    to_set = set([i for i in range(no_to_ids)])

    df = relationship.df

    # Check if one to zero relationships are represented
    from_ids = set(df[relationship.from_table.name + "_id"])
    to_ids = set(df[relationship.to_table.name + "_id"])
    if direction == 0:
        parents_without_children = from_set - from_ids
        parents_with_children = from_ids
        generate_column = relationship.to_table.name + "_id"
    else:
        parents_without_children = to_set - from_ids
        parents_with_children = to_ids
        generate_column = relationship.from_table.name + "_id"

    if not parents_without_children:
        take_out_rows(df, parents_with_children, generate_column)
    if not parents_with_children:
        add_fake_rows(df, parents_without_children, generate_column)


def check_many(relationship, direction):
    # Get the from table and to table
    from_df = relationship.from_table.df
    to_df = relationship.to_table.df

    no_from_ids = len(from_df)
    no_to_ids = len(to_df)

    # create a set with no_from_ids 0 to no_from_ids - 1
    # create a set with no_to_ids 0 to to_from_ids - 1
    from_set = set([i for i in range(no_from_ids)])
    to_set = set([i for i in range(no_to_ids)])

    df = relationship.df

    # Check if one to zero relationships are represented
    from_ids = set(df[relationship.from_table.name + "_id"])
    to_ids = set(df[relationship.to_table.name + "_id"])

    # Check parents with exactly one child
    # Figure out if there are parents with 1 child
    from_with_one_child = set()
    for parent_id in from_set:
        if list(df[relationship.from_table.name + "_id"]).count(parent_id) == 1:
            from_with_one_child.add(parent_id)

    to_with_one_child = set()
    for parent_id in from_set:
        if list(df[relationship.to_table.name + "_id"]).count(parent_id) == 1:
            to_with_one_child.add(parent_id)

    if direction == 0:
        parents_without_children = from_set - from_ids
        parents_with_children = from_ids
        generate_column = relationship.to_table.name + "_id"

        many_parents = from_ids - from_with_one_child - parents_without_children

    else:
        parents_without_children = to_set - from_ids
        parents_with_children = to_ids
        generate_column = relationship.from_table.name + "_id"

        many_parents = to_ids - to_with_one_child - parents_without_children

    if not parents_without_children:
        take_out_rows(df, parents_with_children, generate_column)
    if not parents_with_children:
        add_fake_rows(df, parents_without_children, generate_column)
    if not many_parents:
        add_fake_rows(df, parents_with_children, generate_column)


def adjust_relationships(diagram):
    for relationship in diagram.relationhsips:
        tp = relationship.type

        if tp == RelationshipType.ONE_TO_ONE:
            check_one(relationship.df, 0)
        elif tp == RelationshipType.ONE_TO_MANY:
            check_one(relationship.df, 0)
            check_many(relationship.df, 0)
        elif tp == RelationshipType.MANY_TO_ONE:
            check_one(relationship.df, 1)
            check_many(relationship.df, 1)
        elif tp == RelationshipType.MANY_TO_MANY:
            check_one(relationship.df, 0)
            check_many(relationship.df, 0)
            check_one(relationship.df, 1)
            check_many(relationship.df, 1)
        else:
            raise ValueError(f"Unknown relationship type: {tp}")

def add_fake_rows(df, ids, col):
    # Generate random 10% of ids that were passed
    ids = list(ids)
    no_take_out = len(ids) // 10 if len(ids) // 10 != 0 else 1
    random.shuffle(ids)
    ids = ids[:no_take_out]

    # Add the rows with these ids in the df with the col
    for id in ids:
        # Create columns to get fake distribution from get_fake_row
        tableCols = [{"name": col, "type": df[col].dtype.type} for col in df.columns]
        fake_row = get_fake_row(tableCols)

        new_row = {}
        # Go over the fake row and tableCols and append the fake data according to the fake row
        for i in range(len(fake_row)):
            col_name = tableCols[i]["name"]
            new_row[col_name] = fake_row[i]
        new_row[col] = id
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

def take_out_rows(df, ids, col):
    # Generate random 10% of ids that were passed
    ids = list(ids)
    no_take_out = len(ids) // 10 if len(ids) // 10 != 0 else 1
    random.shuffle(ids)
    ids = ids[:no_take_out]

    # Take out the rows with these ids in the df with the col
    for id in ids:
        df = df[df[col] != id]
