import pandas as pd
from src.dataset import Diagram, Table, Relationship, RelationshipType


def check_one_to_one():
    pass


def adjust_relationships(diagram, dfs, get_fake_row):
     # Get table and relationship data
    from_table_df = table_dfs[relationship.from_table.name]
    to_table_df = table_dfs[relationship.to_table.name]
    relationship_df = relationship_dfs.get(relationship.name, pd.DataFrame())

    # Figure out if there are parents with no children
    parent_ids = set(from_table_df[relationship.from_table.name + "_id"])
    children_ids = set(relationship_df[relationship.to_table.name + "_id"])
    parents_without_children = parent_ids - children_ids

    for relationship in diagram.relationhsips:
        tp = relationship.type

        if tp == RelationshipType.ONE_TO_ONE:
            # Count if 1-1 and 1-0 are both represented
            from_table_df = table_dfs[relationship.from_table.name]
            to_table_df = table_dfs[relationship.to_table.name]
            relationship_df = relationship_dfs.get(relationship.name, pd.DataFrame())
        elif tp == RelationshipType.ONE_TO_MANY:
            pass
        elif tp == RelationshipType.MANY_TO_ONE:
            pass
        elif tp == RelationshipType.MANY_TO_MANY:
            pass
        else:
            raise ValueError(f"Unknown relationship type: {tp}")

def add_fake_rows(diagram, dfs, get_fake_row):
    pass

def take_out_rows(diagram, dfs):
    pass

def adjust_1_to_n_relationships(diagram, dfs, get_fake_row):
    """
    Adjusts rows in tables and relationships to ensure all 1-to-N relationships are properly represented.
    """
    table_dfs = {table.name: df for table, df in dfs if isinstance(table, Table)}
    relationship_dfs = {relationship.name: df for relationship, df in dfs if isinstance(relationship, Relationship)}

    for relationship in diagram.relationships:
        if relationship.type != RelationshipType.ONE_TO_MANY:
            continue  # Skip non-1-to-N relationships

        # Get table and relationship data
        from_table_df = table_dfs[relationship.from_table.name]
        to_table_df = table_dfs[relationship.to_table.name]
        relationship_df = relationship_dfs.get(relationship.name, pd.DataFrame())

        # Figure out if there are parents with no children
        parent_ids = set(from_table_df[relationship.from_table.name + "_id"])
        children_ids = set(relationship_df[relationship.to_table.name + "_id"])
        parents_without_children = parent_ids - children_ids

        # Figure out if there are parents with 1 child
        parents_with_one_child = set()
        for parent_id in parent_ids:
            if list(relationship_df[relationship.from_table.name + "_id"]).count(parent_id) == 1:
                parents_with_one_child.add(parent_id)
        
        # Figure out if there are parents with multiple children
        parents_with_multiple_children = set()
        for parent_id in parent_ids:
            if list(relationship_df[relationship.from_table.name + "_id"]).count(parent_id) > 1:
                parents_with_multiple_children.add(parent_id)
        

        # Add 0 child parents if they don't exist
        if not parents_without_children:
            # Remove children from one parent to make it a 0 child parent
            if parents_with_one_child:
                parent_id = parents_with_one_child.pop()
                child_id = relationship_df[relationship.to_table.name + "_id"][relationship_df[relationship.from_table.name + "_id"] == parent_id].iloc[0]
                relationship_df = relationship_df[relationship_df[relationship.to_table.name + "_id"] != child_id]
            else:
                parent_id = max(parent_ids) + 1

        # Add 1 child parents if they don't exist
        if not parents_with_one_child:
            # Add a child to one parent to make it a 1 child parent
            if parents_without_children:
                parent_id = parents_without_children.pop()
                fake_child = get_fake_row(relationship.to_table.columns)
                fake_child[relationship.to_table.name + "_id"] = parent_id
                relationship_df = relationship_df.append(fake_child, ignore_index=True)
            else:
                parent_id = max(parent_ids) + 1
        
        # Add multiple child parents if they don't exist
        if not parents_with_multiple_children:
            # Add a child to one parent to make it a 1 child parent
            if parents_with_one_child:
                parent_id = parents_with_one_child.pop()
                fake_child = get_fake_row(relationship.to_table.columns)
                fake_child[relationship.to_table.name + "_id"] = parent_id
                relationship_df = relationship_df.append(fake_child, ignore_index=True)
            else:
                parent_id = max(parent_ids) + 1

        # Update DataFrames for child table and relationship
        table_dfs[relationship.to_table.name] = to_table_df
        relationship_dfs[relationship.name] = relationship_df

    # Return updated DataFrames
    updated_dfs = [(table, table_dfs[table.name]) for table in diagram.tables]
    updated_dfs += [(relationship, relationship_dfs[relationship.name]) for relationship in diagram.relationships]
    return updated_dfs
