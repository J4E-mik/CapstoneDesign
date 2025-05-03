import os
import heapq
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict
from sqlalchemy import create_engine, Column, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# 환경변수 설정
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'

# SQLAlchemy 설정
Base = declarative_base()
engine = create_engine(DATABASE_URL, echo=True, future=True)
Session = sessionmaker(bind=engine)
session = Session()

# 테이블 정의
class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True, autoincrement=False)
    type = Column(Integer, nullable=False)
    floor = Column(Integer, nullable=False)

class Edge(Base):
    __tablename__ = 'edges'

    id = Column(Integer, primary_key=True, autoincrement=False)
    weight = Column(Float, nullable=False)
    node1 = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    node2 = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    type = Column(Integer, nullable=False, default=1)

class Routing(Base):
    __tablename__ = 'routing'

    from_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    to_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), primary_key=True)
    to_node_type = Column(Integer, nullable=False)
    next_node_id = Column(Integer, ForeignKey('nodes.id', ondelete='CASCADE'), nullable=False)
    total_cost = Column(Float, nullable=False)

    # ORM 관계 설정 (선택)
    from_node = relationship('Node', foreign_keys=[from_node_id])
    to_node = relationship('Node', foreign_keys=[to_node_id])
    next_node = relationship('Node', foreign_keys=[next_node_id])

# 테이블 초기화 후 생성
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

node_df = pd.read_csv('data/node_table.csv')
edge_df = pd.read_csv('data/edge_table.csv')

node_records = [Node(id=row.id, type=row.type, floor=row.floor) for row in node_df.itertuples(index=False)]
edge_records = [Edge(id=row.id, weight=row.weight, node1=row.node1, node2=row.node2, type=row.type) for row in edge_df.itertuples(index=False)]

session.bulk_save_objects(node_records)
session.bulk_save_objects(edge_records)
session.commit()

# 라우팅 테이블 생성 함수
def build_graph(session):
    edges = session.query(Edge).all()
    graph = defaultdict(list)

    for edge in edges:
        # 양방향 그래프
        graph[edge.node1].append((edge.node2, edge.weight))
        if edge.type == 1:
            graph[edge.node2].append((edge.node1, edge.weight))
    
    return graph

def dijkstra(graph, start_node):
    # 초기화
    dist = {node: float('inf') for node in graph}
    prev = {}
    dist[start_node] = 0
    queue = [(0, start_node)]

    while queue:
        cost, u = heapq.heappop(queue)

        if cost > dist[u]:
            continue

        for v, weight in graph[u]:
            alt = cost + weight
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(queue, (alt, v))

    return dist, prev  # 거리 및 이전 노드 맵 반환

def reconstruct_next_node(prev, start, goal):
    # 목적지가 도달 불가능한 경우
    if goal not in prev:
        return None

    current = goal
    while prev.get(current) != start:
        current = prev.get(current)
        if current is None:
            return None
    return current

def generate_routing_table(session):

    print("그래프 생성 중...")
    graph = build_graph(session)

    print("목적지 후보 노드 추출 중...")
    destinations = session.query(Node).filter(Node.type >= 100).all()
    dest_ids = {d.id: d.type for d in destinations}

    print("다익스트라 수행 중...")
    all_nodes = session.query(Node).all()
    for from_node in all_nodes:
        dist, prev = dijkstra(graph, from_node.id)

        for to_id, to_type in dest_ids.items():
            if to_id == from_node.id:
                continue

            next_node = reconstruct_next_node(prev, from_node.id, to_id)
            if next_node is None or dist[to_id] == float('inf'):
                continue  # 경로 없음

            routing = Routing(
                from_node_id=from_node.id,
                to_node_id=to_id,
                to_node_type=to_type,
                next_node_id=next_node,
                total_cost=dist[to_id]
            )
            session.merge(routing)  # 중복 시 업데이트
        session.commit()
        print(f"✅ from_node {from_node.id} 처리 완료")

    print("라우팅 테이블 생성 완료!")

generate_routing_table(session)