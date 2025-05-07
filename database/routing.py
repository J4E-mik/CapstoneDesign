import heapq
from collections import defaultdict
from database.connection import SessionLocal
from database.models import Node, Edge, Routing

def build_graph(db):
    edges = db.query(Edge).all()
    graph = defaultdict(list)

    for edge in edges:
        graph[edge.node1].append((edge.node2, edge.weight))
        if edge.type == 1:
            graph[edge.node2].append((edge.node1, edge.weight))
    return graph

def dijkstra(graph, start_node):
    dist = {node: float('inf') for node in graph}
    prev = {}
    dist[start_node] = 0
    queue = [(0, start_node)]

    while queue:
        cost, node = heapq.heappop(queue)
        if cost > dist[node]:
            continue
        for adj, weight in graph[node]:
            alt = cost + weight
            if alt < dist[adj]:
                dist[adj] = alt
                prev[adj] = node
                heapq.heappush(queue, (alt, adj))
    return dist, prev

def reconstruct_next_node(prev, start, goal):
    if goal not in prev:
        return None
    node = goal
    while prev.get(node) != start:
        node = prev.get(node)
        if node is None:
            return None
    return node

def generate_routing_table():
    db = SessionLocal()
    graph = build_graph(db)
    destinations = db.query(Node).filter(Node.type >= 100).all()
    dest_ids = {d.id: d.type for d in destinations}
    all_nodes = db.query(Node).all()

    for from_node in all_nodes:
        dist, prev = dijkstra(graph, from_node.id)
        for to_id, to_type in dest_ids.items():
            if to_id == from_node.id:
                continue
            next_node = reconstruct_next_node(prev, from_node.id, to_id)
            if next_node and dist[to_id] != float('inf'):
                routing = Routing(
                    from_node_id=from_node.id,
                    to_node_id=to_id,
                    to_node_type=to_type,
                    next_node_id=next_node,
                    total_cost=dist[to_id]
                )
                db.merge(routing)
        db.commit()
        print(f"{from_node.id} 처리 완료")
    db.close()