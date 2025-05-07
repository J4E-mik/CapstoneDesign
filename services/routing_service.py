from database.connection import SessionLocal
from database.models import Routing, Node
from schemas.schemas import UserSessionResponse
from services.session import user_session

class RoutingService:
    def create_session(self, user_id: str, destination_node_id: int):
        db = SessionLocal()
        routing_info = db.query(Routing).filter(Routing.to_node_id == destination_node_id).all()

        user_session[user_id] = {
            "routing_info": routing_info,
            "destination": destination_node_id,
            "current_step_idx": 0
        }
        return UserSessionResponse(user_id=user_id, status="Session started.")
    
    def end_session(self, user_id:str):
        user_session.pop(user_id, None)
        return UserSessionResponse(user_id=user_id, status="Session ended.")
    
    def initialize_navigation_by_type(self, user_id: str, current_node_id: int, destination_node_type: int):
        db = SessionLocal()

        candiate_destinations = db.query(Node).filter(Node.type == destination_node_type).all()

        if not candiate_destinations:
            db.close()
            return UserSessionResponse(user_id=user_id, status="해당 목적지 타입의 노드를 찾을 수 없습니다.")

        routing_info = None
        min_cost = float('inf')
        
        for dest in candiate_destinations:
            route = db.query(Routing).filter(
                Routing.from_node_id == current_node_id,
                Routing.to_node_id == dest.id
            ).first()
            if route and route.total_cost < min_cost:
                routing_info = route
                min_cost = route.total_cost

        if not routing_info:
            db.close()
            return UserSessionResponse(user_id=user_id, status="경로 정보 없음")
        
        user_session[user_id] = {
            "current_node" : current_node_id,
            "destination_node" : routing_info.to_node_id,
            "next_node": routing_info.next_node_id,
            "total_cost": routing_info.total_cost
        }
        db.close()
        return UserSessionResponse(
            user_id=user_id,
            status=f"다음노드 {routing_info.next_node_id}로 이동",
            next_node=routing_info.next_node_id,
            total_cost=routing_info.total_cost
        )
    
    def get_next_node(self, user_id: str, current_node_id: int):
        if user_id not in user_session:
            if user_id not in user_session:
                return UserSessionResponse(user_id=user_id, status="세션 정보 없음")
            
            destination_node = user_session[user_id]["destination_node"]

            if current_node_id == destination_node:
                user_session.pop(user_id, None)
                return UserSessionResponse(user_id=user_id, status="목적지에 도착했습니다.")
            
            db = SessionLocal()
            routing_info = db.query(Routing).filter(
                Routing.from_node_id == current_node_id,
                Routing.to_node_id == destination_node
            ).first()

            if not routing_info:
                db.close()
                return UserSessionResponse(user_id=user_id, status="다음 경로를 찾을 수 없습니다.")
            
            user_session[user_id].update({
                "current_node" : current_node_id,
                "next_node": routing_info.next_node_id,
                "total_cost": routing_info.total_cost
            })

            db.close()
            return UserSessionResponse(
                user_id=user_id,
                status=f"다음 노드 {routing_info.next_node_id}로 이동"
            )