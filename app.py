from dash import Dash, dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
from SPARQLWrapper import SPARQLWrapper, JSON

app = Dash(__name__)

# Sample movie data for dropdowns
"""
    We need to find a way here to grab this data from a website or database and store it in dataframes that the program AKA the user has then
    access to, when she/he interacts with the program.
"""

movies = ['The Shawshank Redemption', 'The Godfather', 'The Dark Knight', 'Pulp Fiction', 'Forrest Gump']
actors = ['Tim Robbins', 'Morgan Freeman', 'Marlon Brando', 'Al Pacino', 'Christian Bale', 'Heath Ledger', 'John Travolta', 'Uma Thurman', 'Tom Hanks', 'Robin Wright']
directors = ['Frank Darabont', 'Francis Ford Coppola', 'Christopher Nolan', 'Quentin Tarantino', 'Robert Zemeckis']
genres = ['Action', 'Drama', 'Horror', 'Comedy', 'Romance', 'Fantasy']

def query_sparql(search_value):

    sparql = SPARQLWrapper('https://query.wikidata.org/sparql')
    query = """
    SELECT DISTINCT ?item ?itemLabel ?itemDescription WHERE {
        ?item ?label "%s"@en.
        ?item (wdt:P31/wdt:P279*) wd:Q11424.  # Ensure the item is an instance of a film
        ?article schema:about ?item.
        ?article schema:inLanguage "en".
        ?article schema:isPartOf <https://en.wikipedia.org/>.
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
    }
    """ % search_value

    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results
    

app.layout = html.Div([
    html.Div([
        html.Label('Input some movies you watched:'),
        html.Br(),
        dcc.Dropdown(id='movies-dropdown', multi=True, placeholder='Choose movies...'),
        html.Br(),
        html.Div(id='ratings-input-container'),
    ], style={'padding': 10, 'flex': 1}),

    html.Div([
        html.Label('Select your favorite genres:'),
        dcc.Dropdown(id='genres-dropdown', options=[{'label': genre, 'value': genre} for genre in genres], multi=True),
        html.Br(),
        html.Label('Select your favorite actors:'),
        dcc.Dropdown(id='actors-dropdown', options=[{'label': actor, 'value': actor} for actor in actors], multi=True),
        html.Br(),
        html.Label('Select your favorite directors:'),
        dcc.Dropdown(id='directors-dropdown', options=[{'label': director, 'value': director} for director in directors], multi=True),
    ], style={'padding': 10, 'flex': 1}),

    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='output-message', style={'padding': 10}),
], style={'display': 'flex', 'flexDirection': 'row'})

@app.callback(
    Output('ratings-input-container', 'children'),
    [Input('movies-dropdown', 'value')]
)
def update_ratings_input(selected_movies):
    if not selected_movies:
        return []
    return [html.Div([
        html.Label(f'Rating for {movie}:'),
        dcc.Input(id={'type': 'rating-input', 'index': movie}, type='number', min=1, max=5, step=0.1)
    ]) for movie in selected_movies]

@app.callback(
    Output('movies-dropdown', 'options'),
    Input('movies-dropdown', 'search_value'),
    State('movies-dropdown', 'value')
)

def update_dropdown_options(search_value, selected_movies):
    if not search_value:
        raise PreventUpdate
    else:   
        current_values = selected_movies if selected_movies else []
        results = query_sparql(search_value)
        movie_titles = [result['itemLabel']['value'] for result in results['results']['bindings']]
        movie_titles.extend(current_values)
    
    return [{'label': title, 'value': title} for title in movie_titles] 


@app.callback(
    Output('output-message', 'children'),
    [Input('submit-button', 'n_clicks')],
    [State('movies-dropdown', 'value'),
     State({'type': 'rating-input', 'index': ALL}, 'value'),
     State('actors-dropdown', 'value'),
     State('directors-dropdown', 'value'),
     State('genres-dropdown', 'value')]
)
def display_output(n_clicks, selected_movies, ratings, selected_actors, selected_directors, selected_genres):
    if n_clicks > 0:
        if not selected_movies:
            return "Please select at least one movie."
        
        if not ratings:
            return "Please enter ratings for all selected movies."
        
        # Print selected options for testing
        print("Movies you watched:", selected_movies)
        print("\nRatings:", ratings)
        print("\nFavorite Genres:", selected_genres)
        print("\nFavorite Actors:", selected_actors)
        print("\nFavorite Directors:", selected_directors)
        
        # Return a confirmation message
        return html.Div([
            html.Label("You have selected:"),
            html.Br(),
            html.Label(f"\nMovies: {', '.join(selected_movies)}"),
            html.Br(),
            html.Label(f"\nRatings: {', '.join(str(rating) for rating in ratings)}"),
            html.Br(),
            html.Label(f"\nGenres: {', '.join(selected_genres) if selected_genres else 'None'}"),
            html.Br(),
            html.Label(f"\nActors: {', '.join(selected_actors) if selected_actors else 'None'}"),
            html.Br(),
            html.Label(f"\nDirectors: {', '.join(selected_directors) if selected_directors else 'None'}"),
        ])

    raise PreventUpdate

if __name__ == '__main__':
    app.run_server(debug=True)
            
