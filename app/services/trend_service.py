from typing import Dict, Any

def calculate_stats(data_dict: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate statistics (highest, lowest, average) for a data dictionary.
    
    Args:
        data_dict: Dictionary with string keys and integer values
        
    Returns:
        Dictionary containing tertinggi, terendah, and rata_rata statistics
    """
    if not data_dict:
        return {
            "tertinggi": {"nama": "", "jumlah": 0},
            "terendah": {"nama": "", "jumlah": 0},
            "rata_rata": 0
        }
    
    items = list(data_dict.items())
    max_item = max(items, key=lambda x: x[1])
    min_item = min(items, key=lambda x: x[1])
    avg = sum(data_dict.values()) / len(data_dict)
    
    return {
        "tertinggi": {"nama": max_item[0], "jumlah": max_item[1]},
        "terendah": {"nama": min_item[0], "jumlah": min_item[1]},
        "rata_rata": round(avg, 2)
    }
