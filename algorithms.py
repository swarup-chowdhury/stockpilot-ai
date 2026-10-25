from heapq import heappop, heappush


def merge_sort(items, key=lambda x: x):
    """Stable custom merge sort; O(n log n) time and O(n) space."""
    if len(items) <= 1:
        return list(items)
    mid = len(items) // 2
    left = merge_sort(items[:mid], key)
    right = merge_sort(items[mid:], key)
    merged, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    return merged + left[i:] + right[j:]


def binary_search(sorted_items, target, key=lambda x: x):
    """Binary search on data that is already sorted by key; O(log n)."""
    lo, hi = 0, len(sorted_items) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        value = key(sorted_items[mid])
        if value == target:
            return sorted_items[mid]
        if value < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return None


def sku_lookup(products):
    """Hash-based average O(1), worst-case O(n) SKU lookup."""
    return {p["sku"]: p for p in products}


def dijkstra(graph, start):
    """Shortest path with nonnegative edge weights; O((V+E) log V)."""
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    heap = [(0, start)]
    while heap:
        distance, node = heappop(heap)
        if distance != distances[node]:
            continue
        for neighbor, weight in graph[node]:
            if weight < 0:
                raise ValueError("Dijkstra requires nonnegative edge weights")
            candidate = distance + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heappush(heap, (candidate, neighbor))
    return distances, previous


def priority_alerts(recommendations):
    """Min-heap ranking: critical stock gaps first; O(n log n)."""
    heap = []
    for item in recommendations:
        severity = 0 if item.get("status") == "critical" else 1
        heappush(heap, (severity, -float(item.get("suggested_qty", 0)), item["sku"], item))
    return [heappop(heap)[3] for _ in range(len(heap))]


def fefo_batches(batches, needed):
    """First-Expired-First-Out selection; O(n log n) for sorting batches."""
    selected, remaining = [], needed
    for batch in merge_sort(batches, key=lambda b: b.get("expiry_date") or "9999-12-31"):
        if remaining <= 0:
            break
        take = min(remaining, max(0, batch["quantity"]))
        if take:
            selected.append({"batch_id": batch["id"], "quantity": take})
            remaining -= take
    return selected, remaining
