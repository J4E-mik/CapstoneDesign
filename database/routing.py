import heapq
from collections import defaultdict
from database.connection import SessionLocal
from database.models import Node, Edge, Routing

def build_graph(db):
    edges = db.query(Edge).all()
    graph = defaultdict(list)

    for edge in edges:
        graph[edge.node1].append((edge.node2, edge.weight, edge.heuristic))
        if edge.type == 1:
            graph[edge.node2].append((edge.node1, edge.weight, edge.heuristic))
    return graph

def heuristics(graph, node, goal):
    for adj, _, h_value in graph[node]:
        if adj == goal:
            return h_value
        return 0 # 휴리스틱 기본 값 0
    
def a_star(graph, start, goal):
    open_set = [{0, start}]
    came_from = {}
    g_score = {node: float('int') for node in graph}
    g_score[start] = 0

    while open_set:
        current_cost, current_node = heapq.heappop(open_set)

        if current_node == goal:
            break

        for neighbor, weight, _ in graph[current_node]:
            tentative_g_score = g_score[current_node] + weight
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score = tentative_g_score + heuristics(graph, neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return came_from, g_score

def reconstruct_next_node(came_from, start, goal):
    if goal not in came_from:
        return None
    node = goal
    while came_from.get(node) != start:
        node = came_from.get(node)
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
        for to_id, to_type in dest_ids.items():
            if to_id == from_node.id:
                continue
            came_from, g_score = a_star(graph, from_node.id, to_id)
            next_node = reconstruct_next_node(came_from, from_node.id, to_id)
            if next_node and g_score[to_id] != float('inf'):
                routing = Routing(
                    from_node_id=from_node.id,
                    to_node_id=to_id,
                    to_node_type=to_type,
                    next_node_id=next_node,
                    total_cost=g_score[to_id]
                )
                db.merge(routing)
        db.commit()
        print(f"{from_node.id} 처리 완료 (A*)")
    db.close()


# No usage
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