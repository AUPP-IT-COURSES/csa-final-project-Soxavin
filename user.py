class User:
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.favorite_recipes = []  # List to store favorite recipes
