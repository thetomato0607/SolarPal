# Simulate a user database in-memory
user_data = {}

def save_user(user_id, info):
    user_data[user_id] = info

def get_user(user_id):
    return user_data.get(user_id, None)
