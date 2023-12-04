from flask import Flask, render_template, request, session, redirect
import requests
from urllib.parse import unquote
from history import get_user_history, add_to_history
from jinja2 import Environment

# Create the flask app
app = Flask(__name__)

# Set a secret key for the Flask session
app.secret_key = 'AUPPRecipeWebsite'
app.config['SESSION_TYPE'] = 'filesystem'

# Replace with your Spoonacular API key
API_KEY = 'deeaf2c583bc41f28841a6dec3deb1cc'

# Flag to check if it's the first run
first_run = True

# Initialization code to run before each request
@app.before_request
def before_request():
    global first_run
    # Check if it's the first run
    if first_run:
        # Clear the history for a new session
        session['history'] = []
        # Reset the first run flag
        first_run = False

# Define the route for the "Home" button
@app.route('/home', methods=['GET'])
def home():
    # Render the main page with empty recipe list and search query
    return render_template('index.html', recipes=[], search_query='')

# Define the main route for the app
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # If a form is submitted
        query = request.form.get('search_query', '')
        # Perform a search for recipes with the given query
        recipes = search_recipes(query)
        # Render the main page with the search results and the search query
        return render_template('index.html', recipes=recipes, search_query=query)
    
    # If it's a GET request or no form submitted
    search_query = request.args.get('search_query', '')
    decoded_search_query = unquote(search_query)
    # Perform a search for recipes with the decoded search query
    recipes = search_recipes(decoded_search_query)
    # Render the main page
    return render_template('index.html', recipes=recipes, search_query=decoded_search_query)

# Function to get details for a recipe by ID
def get_recipe_details(recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': API_KEY,
        'includeNutrition': False,  # Add this parameter to include ingredients
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        recipe_details = response.json()
        return recipe_details

    print("Failed to get recipe details. Status Code:", response.status_code)
    return None

# Function to search for recipes based on the provided query
def search_recipes(query):
    url = f'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'apiKey': API_KEY,
        'query': query,
        'number': 10,
        'instructionsRequired': True,
        'addRecipeInformation': True,
        'fillIngredients': True,
    }

    # Send a GET request to the Spoonacular API with the query parameters
    response = requests.get(url, params=params)
    # If the API call is successful
    if response.status_code == 200:
        # Parse the API response as JSON data
        data = response.json()
        # Return the list of recipe results
        return data['results']
    # If the API call is not successful
    return []

# Route to view a specific recipe with a given recipe ID
@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    # Get the search query from the URL query parameters
    search_query = request.args.get('search_query', '')
    # Build the URL to get information about the specific recipe ID from Spoonacular API
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'apiKey': API_KEY,
    }

    # Send a GET request to the Spoonacular API to get the recipe information
    response = requests.get(url, params=params)
    # If the API call is successful
    if response.status_code == 200:
        recipe = response.json()
        # Add the recipe to the user's history
        add_to_history({
            'recipe_id': recipe_id,
            'title': recipe['title'],  # Replace with the correct attribute
            'image': recipe['image'],  # Replace with the correct attribute
        })
        return render_template('view_recipe.html', recipe=recipe, search_query=search_query, user_history=get_user_history())
    return "Recipe not found", 404

# Route to display recipe history
@app.route('/history')
def recipe_history():
    # Retrieve the history from the session
    history = get_user_history()

    # Render the history template, passing the recipe details for each ID
    return render_template('history.html', history=history, get_recipe_details=get_recipe_details)

# Function to add a recipe to the user's history
def add_to_history(recipe_info):
    # Retrieve the existing history from the session
    history = get_user_history()

    # Remove duplicates by filtering out recipes with the same ID
    history = [r for r in history if r['recipe_id'] != recipe_info['recipe_id']]

    # Add the new recipe to the beginning of the history list
    history.insert(0, recipe_info)

    # Update the session with the modified history
    session['history'] = history

# Retrieve the history from the session
def get_user_history():
    return session.get('history', [])
def is_dict(obj):
    return isinstance(obj, dict)

@app.route('/share_recipe/<int:recipe_id>')
def share_recipe(recipe_id):
    recipe = get_recipe_details(recipe_id)

    if recipe:
        return render_template('share_recipe.html', recipe=recipe)
    else:
        return "Recipe not found", 404

@app.route('/print/<int:recipe_id>')
def print_recipe(recipe_id):
    recipe = get_recipe_details(recipe_id)
    if recipe:
        return render_template('print_recipe.html', recipe=recipe)
    else:
        return "Recipe not found", 404

# Add the function to the Jinja2 environment
app.jinja_env.globals.update(is_dict=is_dict)

# Run the app in debug mode if executed directly
if __name__ == '__main__':
    app.run(debug=True)
