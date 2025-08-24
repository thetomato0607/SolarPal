# Simulated in-memory user "database"
user_data = {}

def save_user(user_id: str, info: dict):
    """Save or update a user's info."""
    user_data[user_id] = info

def get_user(user_id: str):
    """Retrieve user info by ID, or None if not found."""
    return user_data.get(user_id)
