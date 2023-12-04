
from flask import Flask, session
from flask_session import Session

app = Flask(__name__)

# Set a random secret key for security
app.config['SECRET_KEY'] = 'AUPPRecipeWebsite'

# Use the 'filesystem' session type
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Initialize the Flask-Session extension
Session(app)

def get_user_history():
    # Check if 'history' key exists in the session
    if 'history' not in session:
        # If not, initialize it as an empty list
        session['history'] = []
    # Retrieve the history from the session
    return session['history']

def add_to_history(recipe_info):
    # Retrieve the history from the session
    history = get_user_history()
    # Add the current recipe_info to the history
    history.append(recipe_info)
    # Update the history in the session
    session['history'] = history
