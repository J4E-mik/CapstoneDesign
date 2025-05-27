import pandas as pd
from database.connection import SessionLocal, engine
from database.models import Node, Edge, Base
import math

def safe_float(val):
    return None if pd.isna(val) or (isinstance(val, float) and math.isnan(val)) else val

def seed_data():
    db = SessionLocal()

    node_df = pd.read_csv('data/node_table.csv')
    edge_df = pd.read_csv('data/edge_table.csv')

    nodes = [
        Node(
            id=row.id,
            type=row.type,
            floor=row.floor,
            x=row.x,
            y=row.y
            ) for row in node_df.itertuples(index=False)]
    
    edges = [
        Edge(
            id=row.id,
            weight=row.weight,
            start=row.start,
            end=row.end,
            heuristic=safe_float(row.heuristic),
            type=safe_float(row.type)
            ) for row in edge_df.itertuples(index=False)]

    db.bulk_save_objects(nodes + edges)
    db.commit()
    db.close()

seed_data()