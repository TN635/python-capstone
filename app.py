# to handle user requests
#  User submits player search (First or last name).
#  Fetch player data from the API based on search query.
#  If player exists it will display the player data and stats form.
#  If no player is found it will return a No player found message.

# to display player stats
#  Display players name, team, and position.
#  Provide a dropdown to select a season.
#  Display player stats for the selected season.
#  If user selects a season and submit it will fetch the stats for that season.

#Fetch player Stats
#  User selects a season.
#  Fetch players stats from the API for that selected season.
#  If stats are available it will display them (points per game, assists, and so on).
#  If no stats are found for the selected season it will display a No stats available message.


from flask import Flask, render_template, request, redirect, url_for
import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote
import random

app = Flask(__name__)

# Load API key from .env
load_dotenv()
api_key = os.getenv('API_KEY')

# Global variable to store favorite player IDs
favorites = []

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/player')
def player():
    player_name = request.args.get('player_name')

    if not player_name:
        return "Player name cannot be empty. Please enter a valid name."

    player_name_encoded = quote(player_name.strip())
    api_url = f"https://api.balldontlie.io/v1/players?search={player_name_encoded}"

    headers = {
        'Authorization': api_key
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        return f"Error: Unable to fetch data from API (Status Code: {response.status_code})"

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "Error: API returned invalid JSON."

    if not data['data']:
        return f"No player found with the name '{player_name}'."

    players = data['data']

    return render_template('players.html', players=players)


@app.route('/add-to-favorites', methods=['POST'])
def add_to_favorites():
    player_id = request.form.get('player_id')


    if player_id and player_id not in favorites:
        favorites.append(player_id)

    return redirect(url_for('favorites_page'))  # Change here


@app.route('/favorites')
def favorites_page():
    if not favorites:
        return render_template('favorites.html', favorites=[])

    players_data = []
    for player_id in favorites:
        api_url = f"https://api.balldontlie.io/v1/players/{player_id}"
        headers = {'Authorization': api_key}
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            return f"Error: Unable to fetch player data (Status Code: {response.status_code})"

        try:
            player = response.json()['data']
            players_data.append(player)
        except requests.exceptions.JSONDecodeError:
            return "Error: API returned invalid JSON."

    return render_template('favorites.html', players=players_data)


@app.route('/remove-from-favorites', methods=['POST'])
def remove_from_favorites():
    player_id = request.form.get('player_id')

    if player_id in favorites:
        favorites.remove(player_id)

    return redirect(url_for('favorites_page'))


@app.route('/player/<int:player_id>/season-stats')
def season_stats(player_id):
    season = request.args.get('season')

    if not season:
        return "Error: Season not specified. Please select a valid season."

    api_url = "https://api.balldontlie.io/v1/season_averages"


    params = {
        "season": season,
        "player_id": player_id
    }

    headers = {
        'Authorization': api_key
    }


    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code != 200:
        return f"Error: Unable to fetch season stats (Status Code: {response.status_code})"

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return f"Error: API returned invalid JSON. Raw Response: {response.text}"


    if not data['data']:
        return f"No season stats found for player ID {player_id} in season {season}."


    stats = data['data'][0]


    player_api_url = f"https://api.balldontlie.io/v1/players/{player_id}"
    player_response = requests.get(player_api_url, headers=headers)

    if player_response.status_code != 200:
        return f"Error: Unable to fetch player data (Status Code: {player_response.status_code})"

    player_data = player_response.json()['data']

    return render_template('season_stats.html', player=player_data, stats=stats, season=season)


@app.route('/random-player')
def random_player():
    random_page = random.randint(1, 215)
    random_page_url = f"https://api.balldontlie.io/v1/players?per_page=25&page={random_page}"
    headers = {
        'Authorization': api_key
    }

    response = requests.get(random_page_url, headers=headers)

    if response.status_code != 200:
        return f"Error: Unable to fetch random player page (Status Code: {response.status_code})"

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return "Error: API returned invalid JSON."

    players_on_page = data.get('data', [])
    if not players_on_page:
        return "No players found on this page."

    random_player = random.choice(players_on_page)

    return render_template('random_player.html', player=random_player)


if __name__ == "__main__":
    app.run(debug=True)
