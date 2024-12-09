import pandas as pd
from er_diagram import RelationshipType
import random
from fake_data import get_fake_rows


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
        parent_column = relationship.from_table.name + "_id"
        child_column = relationship.to_table.name + "_id"
        child_random = no_to_ids
    else:
        parents_without_children = to_set - from_ids
        parents_with_children = to_ids
        parent_column = relationship.to_table.name + "_id"
        child_column = relationship.from_table.name + "_id"
        child_random = no_from_ids

    if not parents_without_children:
        df = take_out_rows(df, parents_with_children, parent_column)
    if not parents_with_children:
        df = add_fake_rows(df, parents_without_children,
                           parent_column, child_column, child_random)
    return df


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

    # Check parents with exactly one child
    # Figure out if there are parents with 1 child
    from_with_many_child = set()
    from_with_one_child = set()
    for parent_id in from_set:
        if list(df[relationship.from_table.name + "_id"]).count(parent_id) == 1:
            from_with_one_child.add(parent_id)
        elif list(df[relationship.from_table.name + "_id"]).count(parent_id) > 1:
            from_with_many_child.add(parent_id)
    
    to_with_many_child = set()
    to_with_one_child = set()
    for parent_id in to_set:
        if list(df[relationship.to_table.name + "_id"]).count(parent_id) == 1:
            to_with_one_child.add(parent_id)
        elif list(df[relationship.to_table.name + "_id"]).count(parent_id) > 1:
            to_with_many_child.add(parent_id)

    if direction == 0:
        parents_with_many_child = from_with_many_child
        parents_with_one_child = from_with_one_child
        parent_column = relationship.from_table.name + "_id"
        child_column = relationship.to_table.name + "_id"
        child_random = no_to_ids
    else:
        parents_with_many_child = to_with_many_child
        parents_with_one_child = to_with_one_child
        parent_column = relationship.to_table.name + "_id"
        child_column = relationship.from_table.name + "_id"
        child_random = no_from_ids

    if not parents_with_many_child:
        df = add_fake_rows(df, parents_with_one_child, parent_column, child_column, child_random)
    return df


def adjust_relationships(diagram):
    for relationship in diagram.relationships:
        print("before adjusting relationship")
        print(relationship.df)
        print("relationship type", relationship.type)
        print()
        tp = relationship.type
        if tp.value == 1:
            relationship.df = check_one(relationship, 0)
        elif tp.value == 2:
            relationship.df = check_one(relationship, 0)
            relationship.df = check_many(relationship, 0)
        elif tp.value == 3:
            relationship.df = check_one(relationship, 1)
            relationship.df = check_many(relationship, 1)
        elif tp.value == 4:
            relationship.df = check_one(relationship, 0)
            relationship.df = check_one(relationship, 1)
            relationship.df = check_many(relationship, 0)
            relationship.df = check_many(relationship, 1)
        else:
            raise ValueError(f"Unknown relationship type: {tp}")

        print("after adjusting relationship", relationship.df)
        print(relationship.df)


def add_fake_rows(df, ids, par_col, child_col, child_random, many = 0):
    # Generate random 10% of ids that were passed
    ids = list(ids)
    no_take_out = len(ids) // 10 if len(ids) // 10 != 0 else 1
    random.shuffle(ids)
    ids = ids[:no_take_out]

    print("adding fake rows", ids)
    # Add the rows with these ids in the df with the col
    # Create columns to get fake distribution from get_fake_row
    tableCols = [{"name": col, "type": df[col].dtype.type}
                 for col in df.columns]
    fake_rows = get_fake_rows(tableCols, len(ids))
    child_set = set()
    for i in range(len(ids)):
        id = ids[i]
        fake_row = fake_rows[i]
        new_row = {}
        
        # Go over the fake row and tableCols and append the fake data according to the fake row
        for i in range(len(fake_row)):
            col_name = tableCols[i]["name"]
            new_row[col_name] = fake_row[i]
        new_row[par_col] = id

        # Generate a random number for the child column until it is unique
        new_row[child_col] = random.randint(0, child_random)
        while new_row[child_col] in child_set:
            new_row[child_col] = random.randint(0, child_random)
        child_set.add(new_row[child_col])
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # if many:
        #     # Choose a random number of children to add
        #     no_children = random.randint(1, 3)
        #     # for i in range(no_children):
        #     new_row = {}
        #     for i in range(len(fake_row)):
        #         col_name = tableCols[i]["name"]
        #         new_row[col_name] = fake_row[i]
        #     new_row[par_col] = id
        #     new_row[child_col] = random.randint(0, child_random)
        #     while new_row[child_col] in child_set:
        #         new_row[child_col] = random.randint(0, child_random)
        #     child_set.add(new_row[child_col])
        #     df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    return df


def take_out_rows(df, ids, col):
    # Generate random 10% of ids that were passed
    ids = list(ids)
    no_take_out = len(ids) // 20 if len(ids) // 20 != 0 else 1
    random.shuffle(ids)
    ids = ids[:no_take_out]

    print("taking out rows", ids)
    # Take out the rows with these ids in the df with the col

    for id in ids:
        df = df[df[col] != id]

    return df
