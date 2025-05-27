from database.heuristic import update_heuristics

class FeedbackService:
    def __init__(self):
        self.edge_usage_data={}

    def record_edge_usage(self, edge_id, usage_time):
        self.edge_usage_data.setdefault(edge_id, []).append(usage_time)
    
    def update_database(self):
        update_heuristics(self.edge_usage_data)
        self.edge_usage_data.clear()

feedback_service = FeedbackService()

def user_passed_edge(edge_id, usage_time):
    feedback_service.record_edge_usage(edge_id, usage_time)