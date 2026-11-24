"""Các thuật toán đồ thị dùng trong hệ thống đường sắt Bling Candy.
""fix tiep adu""
Module này chỉ xử lý dữ liệu, không phụ thuộc vào Tkinter hay giao diện.
"""
import math


class DSU:
    """Disjoint Set Union, hỗ trợ phát hiện chu trình trong Kruskal."""

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return False
        if self.rank[root_a] < self.rank[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        if self.rank[root_a] == self.rank[root_b]:
            self.rank[root_a] += 1
        return True


def kruskal(stations, edges):
    """Tìm MST trên các nhà ga và tuyến đường đang hoạt động.

    Trả về dictionary gồm danh sách ga hoạt động, ga hỏng, cạnh hợp lệ,
    cạnh MST được chọn, tổng trọng số và trạng thái liên thông.
    """
    active_stations = [station for station in stations if not station.broken]
    broken_stations = [station for station in stations if station.broken]
    active_ids = {station.id for station in active_stations}
    usable_edges = [
        edge for edge in edges
        if not edge.broken and edge.u in active_ids and edge.v in active_ids
    ]

    if not active_stations:
        return {
            "active_stations": active_stations,
            "broken_stations": broken_stations,
            "usable_edges": usable_edges,
            "selected_edges": [],
            "total_weight": 0,
            "connected": False,
        }

    if len(active_stations) == 1:
        return {
            "active_stations": active_stations,
            "broken_stations": broken_stations,
            "usable_edges": usable_edges,
            "selected_edges": [],
            "total_weight": 0,
            "connected": True,
        }

    ids = [station.id for station in active_stations]
    index = {station_id: i for i, station_id in enumerate(ids)}
    dsu = DSU(len(ids))
    selected_edges = []
    total_weight = 0

    for edge in sorted(usable_edges, key=lambda item: item.weight):
        if dsu.union(index[edge.u], index[edge.v]):
            selected_edges.append(edge)
            total_weight += edge.weight
            if len(selected_edges) == len(active_stations) - 1:
                break

    return {
        "active_stations": active_stations,
        "broken_stations": broken_stations,
        "usable_edges": usable_edges,
        "selected_edges": selected_edges,
        "total_weight": total_weight,
        "connected": len(selected_edges) == len(active_stations) - 1,
    }


def dijkstra(stations, edges, start_id, end_id):
    """Tìm đường đi ngắn nhất giữa hai ga đang hoạt động.

    Trọng số phải không âm. Thuật toán dùng phép quét danh sách chưa thăm,
    phù hợp với quy mô đồ thị nhỏ của chương trình mô phỏng.
    """
    if any(edge.weight < 0 for edge in edges):
        return {"status": "negative_weight", "path": [], "path_edges": [], "distance": math.inf}

    active_ids = {station.id for station in stations if not station.broken}
    if start_id not in active_ids or end_id not in active_ids:
        return {"status": "invalid_station", "path": [], "path_edges": [], "distance": math.inf}

    adjacency = {station_id: [] for station_id in active_ids}
    for edge in edges:
        if edge.broken or edge.u not in active_ids or edge.v not in active_ids:
            continue
        adjacency[edge.u].append((edge.v, edge.weight, edge))
        adjacency[edge.v].append((edge.u, edge.weight, edge))

    distances = {station_id: math.inf for station_id in active_ids}
    previous = {}
    previous_edge = {}
    visited = set()
    distances[start_id] = 0

    while True:
        current = None
        current_distance = math.inf
        for station_id, distance in distances.items():
            if station_id not in visited and distance < current_distance:
                current = station_id
                current_distance = distance
        if current is None or current_distance == math.inf:
            break
        if current == end_id:
            break
        visited.add(current)
        for neighbor, weight, edge in adjacency[current]:
            if neighbor in visited:
                continue
            new_distance = distances[current] + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current
                previous_edge[neighbor] = edge

    if distances[end_id] == math.inf:
        return {"status": "unreachable", "path": [], "path_edges": [], "distance": math.inf}

    path = [end_id]
    path_edges = []
    current = end_id
    while current != start_id:
        path_edges.append(previous_edge[current])
        current = previous[current]
        path.append(current)
    path.reverse()
    path_edges.reverse()

    return {
        "status": "ok",
        "path": path,
        "path_edges": path_edges,
        "distance": distances[end_id],
    }
