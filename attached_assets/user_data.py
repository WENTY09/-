from datetime import datetime, timedelta
from typing import Dict, Tuple, List, Any, Optional
import json
import os
import logging

# File to save/load user data
DATA_FILE = "delivery_user_data.json"

# Configure logging
logger = logging.getLogger(__name__)

# In-memory storage for user data
user_data: Dict[int, Dict[str, Any]] = {}

# Shop items definitions
SHOP_ITEMS = [
    {
        "id": "hyper_buff",
        "name": "Гипер Бафф",
        "description": "Повышает доход на 50%",
        "price": 2750,
        "duration_minutes": 40,
        "earning_multiplier": 0.5,
        "image_path": "attached_assets/IMG_2284.jpeg"
    },
    {
        "id": "super_buff",
        "name": "Супер Бафф",
        "description": "Повышает доход на 15%",
        "price": 850,
        "duration_minutes": 30,
        "earning_multiplier": 0.15,
        "image_path": "attached_assets/IMG_2283.jpeg"
    },
    {
        "id": "mega_buff",
        "name": "Мега Бафф",
        "description": "Повышает доход на 25%",
        "price": 1800,
        "duration_minutes": 30,
        "earning_multiplier": 0.25,
        "image_path": "attached_assets/IMG_2282.jpeg"
    }
]

def _load_data() -> None:
    """Load user data from file if it exists."""
    global user_data
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                # Convert string keys back to integers
                user_data = {int(k): v for k, v in loaded_data.items()}
                
                # Convert string timestamps back to datetime objects
                for user_info in user_data.values():
                    if user_info.get("last_delivery"):
                        user_info["last_delivery"] = datetime.fromisoformat(user_info["last_delivery"])
                    
                    # Convert active buffs timestamps
                    if "active_buffs" in user_info:
                        for buff in user_info["active_buffs"]:
                            if buff.get("expires_at"):
                                buff["expires_at"] = datetime.fromisoformat(buff["expires_at"])
    except Exception as e:
        logger.error(f"Error loading data: {e}")

def _save_data() -> None:
    """Save user data to file."""
    try:
        # Convert datetime objects to string for JSON serialization
        serializable_data = {}
        for user_id, user_info in user_data.items():
            user_copy = user_info.copy()
            
            # Convert last_delivery timestamp
            if user_copy.get("last_delivery"):
                user_copy["last_delivery"] = user_copy["last_delivery"].isoformat()
            
            # Convert active buffs timestamps
            if "active_buffs" in user_copy:
                for buff in user_copy["active_buffs"]:
                    if buff.get("expires_at"):
                        buff["expires_at"] = buff["expires_at"].isoformat()
                        
            serializable_data[str(user_id)] = user_copy
            
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving data: {e}")

# Load data when module is imported
_load_data()

def get_user_data(user_id: int) -> Dict[str, Any]:
    """Get user data or initialize if it doesn't exist."""
    if user_id not in user_data:
        user_data[user_id] = {
            "total_deliveries": 0,
            "total_earnings": 0,
            "experience": 0,
            "last_delivery": None,
            "active_buffs": []
        }
    
    # Ensure active_buffs exists for backward compatibility
    if "active_buffs" not in user_data[user_id]:
        user_data[user_id]["active_buffs"] = []
        
    return user_data[user_id]

def update_user_data(user_id: int, deliveries: int, earnings: int) -> Tuple[int, int]:
    """
    Update user data after a delivery.
    
    Returns:
        Tuple of (original_earnings, buffed_earnings)
    """
    data = get_user_data(user_id)
    
    # Apply buffs to earnings if any are active
    total_multiplier = get_active_earnings_multiplier(user_id)
    buffed_earnings = int(earnings * (1 + total_multiplier))
    
    # Update user data
    data["total_deliveries"] += deliveries
    data["total_earnings"] += buffed_earnings
    data["experience"] += 1
    data["last_delivery"] = datetime.now()
    
    # Save after updates
    _save_data()
    
    # Return both original and buffed earnings
    return earnings, buffed_earnings

def can_deliver(user_id: int) -> Tuple[bool, Optional[timedelta]]:
    """Check if a user can make a delivery (2-minute cooldown)."""
    data = get_user_data(user_id)
    last_delivery = data.get("last_delivery")
    
    if last_delivery is None:
        return True, None
    
    cooldown = timedelta(minutes=2)
    now = datetime.now()
    time_passed = now - last_delivery
    
    if time_passed < cooldown:
        time_remaining = cooldown - time_passed
        return False, time_remaining
    
    return True, None

def get_top_users(limit: int = 5) -> List[Tuple[int, str, int]]:
    """Get the top users by number of deliveries."""
    # Sort users by total deliveries in descending order
    sorted_users = sorted(
        user_data.items(),
        key=lambda x: x[1]["total_deliveries"],
        reverse=True
    )
    
    # Return the top users with their delivery count
    return [(user_id, data.get("username", "Unknown"), data["total_deliveries"]) 
            for user_id, data in sorted_users[:limit]]

def get_shop_item(index: int) -> Dict[str, Any]:
    """Get shop item by index."""
    # Ensure index is within bounds
    index = index % len(SHOP_ITEMS)
    return SHOP_ITEMS[index]

def purchase_buff(user_id: int, item_index: int) -> Tuple[bool, str]:
    """
    Attempt to purchase a buff for the user.
    
    Returns:
        Tuple of (success, message)
    """
    user_data_entry = get_user_data(user_id)
    shop_item = get_shop_item(item_index)
    
    # Check if user has enough money
    if user_data_entry.get("total_earnings", 0) < shop_item["price"]:
        return False, f"❌ Недостаточно средств! Нужно: {shop_item['price']} рублей."
    
    # Subtract cost
    user_data_entry["total_earnings"] -= shop_item["price"]
    
    # Add buff to active buffs
    now = datetime.now()
    expires_at = now + timedelta(minutes=shop_item["duration_minutes"])
    
    buff_data = {
        "id": shop_item["id"],
        "name": shop_item["name"],
        "multiplier": shop_item["earning_multiplier"],
        "purchased_at": now,
        "expires_at": expires_at
    }
    
    user_data_entry["active_buffs"].append(buff_data)
    
    # Save changes
    _save_data()
    
    return True, f"✅ Вы приобрели {shop_item['name']} на {shop_item['duration_minutes']} минут!"

def get_active_earnings_multiplier(user_id: int) -> float:
    """
    Calculate the total earnings multiplier from all active buffs.
    
    Returns:
        Float multiplier (e.g., 0.25 for 25% increase)
    """
    data = get_user_data(user_id)
    now = datetime.now()
    
    # Initialize multiplier
    total_multiplier = 0.0
    
    # Filter out expired buffs and sum multipliers of active ones
    active_buffs = []
    for buff in data.get("active_buffs", []):
        if "expires_at" in buff and buff["expires_at"] > now:
            active_buffs.append(buff)
            total_multiplier += buff.get("multiplier", 0)
    
    # Replace the list with only active buffs
    data["active_buffs"] = active_buffs
    
    # Save if we removed any expired buffs
    if len(active_buffs) != len(data.get("active_buffs", [])):
        _save_data()
    
    return total_multiplier

def get_active_buffs_info(user_id: int) -> List[Dict[str, Any]]:
    """
    Get information about active buffs for display purposes.
    
    Returns:
        List of active buffs with name and remaining time
    """
    data = get_user_data(user_id)
    now = datetime.now()
    active_buffs_info = []
    
    for buff in data.get("active_buffs", []):
        if "expires_at" in buff and buff["expires_at"] > now:
            remaining = buff["expires_at"] - now
            remaining_minutes = int(remaining.total_seconds() // 60)
            remaining_seconds = int(remaining.total_seconds() % 60)
            
            buff_info = {
                "name": buff.get("name", "Неизвестный бафф"),
                "multiplier": buff.get("multiplier", 0),
                "remaining_minutes": remaining_minutes,
                "remaining_seconds": remaining_seconds
            }
            active_buffs_info.append(buff_info)
    
    return active_buffs_info
