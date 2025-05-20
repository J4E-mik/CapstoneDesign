from database.heuristic import update_heuristic
from database.routing import generate_routing_table

class FeedbackService:
    def __init__(self):
        self.edge_usage_data={}

    def record_edge_usage(self, edge_id, usage_time):
        self.edge_usage_data.setdefault(edge_id, []).append(usage_time)
    
    def update_database_and_routing(self):
        update_heuristic(self.edge_usage_data)
        generate_routing_table()
        self.edge_usage_data.clear()