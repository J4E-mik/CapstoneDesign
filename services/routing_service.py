from database.connection import SessionLocal
from database.models import Node, Edge
from schemas.schemas import UserSessionResponse
from services.session import user_session
from services.feedback_service import FeedbackService
from collections import defaultdict
import numpy as np
import heapq

feedback_service = FeedbackService()

def user_passed_edge(edge_id, usage_time):
    feedback_service.record_edge_usage(edge_id, usage_time)

def periodic_feedback_update():
    feedback_service.update_database_and_routing()

class RoutingService:
    def store_user_itinerary(self, user_id:str, itinerary: dict):
        user_session[user_id]={
            "itinerary": itinerary,
            "current_leg_idx":0,
            "current_step_idx":0
        }
        
    def end_session(self, user_id:str):
        user_session.pop(user_id, None)
        return UserSessionResponse(user_id=user_id, status="Session ended.")
    
    def initialize_subway_navigation(
        self,
        user_id: str,
        start_node_id: int,
        goal_node_id: int
    ):
        db = SessionLocal()

        nodes = db.query(Node).all()
        node_coords = {node.id:(node.x, node.y) for node in nodes}

        edges = db.query(Edge).all()
        graph = defaultdict(list)
        for edge in edges:
            graph[edge.start].append((edge.end, edge.weight, edge.heuristic))

        came_from, _ = self.a_star(graph, start_node_id, goal_node_id)
        if goal_node_id not in came_from:
            db.close()
            return {"error": "Path 탐색 실패"}
        
        path = self.reconstruct_path(came_from, start_node_id, goal_node_id)
        route_response = self.build_json_response(path, node_coords)

        user_session[user_id] = {"current_path": path}
        db.close()
        return route_response
    
    def a_star(self, graph, start, goal):
        open_set=[]
        heapq.heappush(open_set, (0,start))
        came_from = {}
        g_score = defaultdict(lambda:float('inf'))
        g_score[start] = 0

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                break

            for neighbor, weight, heuristic in graph[current]:
                tentative_g_score = g_score[current] + weight
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic
                    heapq.heappush(open_set, (f_score, neighbor))
                
            return came_from, g_score
        
    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
    
    def build_json_response(self, path, node_coords):
        steps = []

        steps.append({
            "prev": None,
            "current": path[0],
            "next": path[1],
            "direct": 2
        })

        for i in range(1, len(path)-1):
            prev, current, next_ = path[i-1], path[i], path[i+1]
            direction = self.calculate_direction(node_coords[prev], node_coords[current], node_coords[next_])
            steps.append({
                "prev": prev,
                "current":current,
                "next": next_,
                "direct": direction
            })

        return {
            "start": path[0],
            "goal":path[-1],
            "steps":steps
        }
    
    def calculate_direction(self, coord_prev, coord_current, coord_next):
        v1 = np.array(coord_current) - np.array(coord_prev)
        v2 = np.array(coord_next) - np.array(coord_current)
        cross_product = np.cross(v1,v2)

        if cross_product > 0:
            return 1 # left
        elif cross_product <0:
            return 3 # right
        else:
            return 2 #straight