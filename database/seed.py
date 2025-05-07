import pandas as pd
from database.connection import SessionLocal
from database.models import Node, Edge

def seed_data():
    db = SessionLocal()

    node_df = pd.read_csv('data/node_table.csv')
    edge_df = pd.read_csv('data/edge_table.csv')

    nodes = [Node(id=row.id, type=row.type, floor=row.floor) for row in node_df.itertuples(index=False)]
    edges = [Edge(id=row.id, weight=row.weight, node1=row.node1, node2=row.node2, type=row.type) for row in edge_df.itertuples(index=False)]

    db.bulk_save_objects(nodes + edges)
    db.commit()
    db.close()