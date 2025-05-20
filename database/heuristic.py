from database.connection import SessionLocal
from database.models import Edge

TYPE_COST_MAP = {1:10, 2:1}

def compute_heuristic(edge, actual_avg_time=None):
    base_time = edge.weight / 2
    type_cost = TYPE_COST_MAP.get(edge.type, 0)
    heuristic = base_time + type_cost

    if actual_avg_time and actual_avg_time > base_time:
        delay_feedback = min(actual_avg_time - base_time, 20)
        heuristic += delay_feedback

    return heuristic

def update_heuristics(edge_usage_data=None):
    db = SessionLocal()
    edges = db.query(Edge).all()

    for edge in edges:
        actual_avg_time = None
        if edge_usage_data and edge.id in edge_usage_data:
            times = edge_usage_data[edge.id]
            actual_avg_time = sum(times)/len(times)

        edge.heuristic = compute_heuristic(edge, actual_avg_time)
    
    db.commit()
    db.close()