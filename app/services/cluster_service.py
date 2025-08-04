from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def group_and_count(data: list, group_key: str) -> list[dict]:
    """Group data and count occurrences"""
    counts = {}
    
    for item in data:
        key = get_nested_value(item, group_key)
        if key is not None:  # Only count non-None keys
            counts[key] = counts.get(key, 0) + 1
    
    return [{"name": k, "count": v} for k, v in counts.items() if k is not None]

def get_nested_value(obj: dict, path: str):
    """Access nested dictionary keys"""
    keys = path.split('.')
    # print(f"Getting nested value for path: {path}, keys: {keys}")
    # print(f"Initial obj: {obj}")
    
    for i, key in enumerate(keys):
        # print(f"Step {i}: key='{key}', obj type: {type(obj)}, obj: {obj}")
        if obj is None or not isinstance(obj, dict):
            # print(f"Returning None at step {i} because obj is None or not dict")
            return None
        obj = obj.get(key, {})
        # print(f"After get('{key}'): {obj}")
    
    result = obj if obj != {} else None
    # print(f"Final result: {result}")
    return result

def perform_clustering(data: list[dict]) -> list[dict]:
    """Perform KMeans clustering on crime data"""
    if not data:
        return []

    # Prepare data for clustering
    counts = [d['count'] for d in data]
    scaler = MinMaxScaler()
    normalized_counts = scaler.fit_transform([[x] for x in counts])
    
    # Cluster into 3 levels
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(normalized_counts)
    
    # Map clusters to levels
    cluster_means = {}
    for i, cluster in enumerate(clusters):
        cluster_means[cluster] = cluster_means.get(cluster, 0) + counts[i]
    
    sorted_clusters = sorted(cluster_means.items(), key=lambda x: x[1])
    level_map = {
        sorted_clusters[0][0]: "Rendah",
        sorted_clusters[1][0]: "Sedang",
        sorted_clusters[2][0]: "Tinggi"
    }
    
    # Add cluster info to each item
    for i, item in enumerate(data):
        item['level'] = level_map[clusters[i]]
        item['normalized_count'] = float(normalized_counts[i][0])
    
    return data