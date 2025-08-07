import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import streamlit as st
import pandas as pd
import re
import requests

# Main script
############################### Header ########################################

st.title("Pimp my track :sunglasses:")

############################### GET TOP TRACKS ########################################

# Get user top tracks

def api_spotify_auth(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_id, client_secret= cred.client_secret, redirect_uri=cred.redirect_url, scope=scope))
    return sp

def get_top_tracks(time_range, track_nb, offset, sp):

    # API result
    top_tracks = sp.current_user_top_tracks(limit=track_nb, offset=offset, time_range=time_range)
    
    # Create dataframe and list of ids
    track_details = []
    track_number = len(top_tracks["items"])
    track_ids = []
    print(track_number)

    for i in range(track_number):
        track_name = top_tracks['items'][i]['name']
        track_artists = top_tracks['items'][i]['artists'][0]['name']
        track_url = top_tracks['items'][i]['external_urls']['spotify']
        track_id = top_tracks['items'][i]['id']

        track_details.append({
                    "Title": track_name,
                    "Artist": track_artists,
                    "URL": track_url
                    #"ID" : track_id
                })
        track_ids.append(track_id)

    df_tracks = pd.DataFrame(track_details)
    
    #replace by st.dataframe
    st.dataframe(df_tracks)
    
    return track_ids

st.header("Let's get your Spotify top tracks", divider = 'green')
# widget to choose between long / medium / short term
st.write('The recommended tracks will be based on your Spotify top tracks, as well as track features such as danceability or popularity, that you will be able to tune a little further.')
time_range= st.pills("Spotify listening period:", ['short_term', 'medium_term', 'long_term'])

# Other args
track_nb = 5
offset = 0
scope = "user-top-read"

sp = api_spotify_auth(scope)

track_ids = get_top_tracks(time_range, track_nb, offset, sp)

# st.write(track_ids)

############################### RECOMMENDATION ########################################
# Reccobeats 
# Get recommendations

def build_params(seeds):
    
    # Define param for each feature with widgets
    #0 to 1
    st.header("Now, tune it your way", divider = 'green')
    enable_sliders = st.toggle("Select track features")
    if enable_sliders:
        acousticness = st.slider("Acousticness :", 0.0, 1.0, 0.2)
        danceability = st.slider("Danceability :", 0.0, 1.0, 0.2)
        energy = st.slider("Energy :", 0.0, 1.0, 0.2)
        instrumentalness = st.slider("Instrumentalness :", 0.0, 1.0, 0.2)
        liveness = st.slider("Liveness :", 0.0, 1.0, 0.2)
        speechiness = st.slider("Speechiness :", 0.0, 1.0, 0.2)
        valence = st.slider("Valence :", 0.0, 1.0, 0.2)
    else:
        acousticness = None
        danceability = None
        energy = None
        instrumentalness = None
        liveness = None
        speechiness = None
        valence = None

    # 1 (Major) or 0 (Minor)
    options = ["Whatever", "Major", "Minor" ]
    mode = st.pills("Mode", options)
    mode_mapping ={
        "Whatever": None,
        "Major": 1,
        "Minor":0
    }
    mode = mode_mapping.get(mode)

    # -1 to 11
    options = ["Whatever","C", "C♯/D♭", "D", "D♯/E♭", "E", "F", "F♯/G♭", "G", "G♯/A♭", "A", "A♯/B♭", "B"]
    key = st.pills("Key", options)
    pitch_class_notation = {
        "Whatever" : None,
        "C": 0,
        "C♯/D♭": 1,
        "D": 2,
        "D♯/E♭": 3,
        "E": 4,
        "F": 5,
        "F♯/G♭": 6,
        "G": 7,
        "G♯/A♭": 8,
        "A": 9,
        "A♯/B♭": 10,
        "B": 11
    }
    key = pitch_class_notation.get(key)

    # 0 to 250 (BPM)
    enable_tempo = st.toggle("Select track tempo")
    if enable_tempo:
        tempo = st.slider("Tempo :", 1, 250, 1)
    else:
        tempo = None

    # 0 to 100
    popularity = st.slider("Popularity of the tracks :", 1, 100, 1)

    # Can be 1 to 100
    # size = st.number_input("Insert a number of track", min_value = 1, max_value = 100)
    size = 10

    #Initialize params dico
    recommended_track_params = {
        'size' : size, 
        'seeds': seeds,
    }

    # Build params dico
    all_params = {
        'acousticness': acousticness,
        'danceability': danceability,
        'energy': energy,
        'instrumentalness': instrumentalness,
        'liveness': liveness,
        'speechiness': speechiness,
        'valence': valence,
        'mode': mode,
        'key': key,
        'tempo': tempo,
        'popularity': popularity
    }

    # Add params to final dico where value is not None
    for param_name, param_value in all_params.items():
        if param_value is not None:
            recommended_track_params[param_name] = param_value
    
    return recommended_track_params


def get_recommendation(url, recommended_track_params):
    # Get API response
    response = requests.get(url, params=recommended_track_params)
    recommended_track = response.json()
    
    recommended_track_number = len(recommended_track["content"])
    # st.write(recommended_track_number)

    # Create dataframe with recommended tracks
    recommended_track_details = []
    for i in range(recommended_track_number):
        recommended_track_name = recommended_track['content'][i]['trackTitle']
        recommended_track_artist = recommended_track['content'][i]['artists'][0]['name']
        recommended_track_spotify_url = recommended_track['content'][i]['href']
        recommended_track_details.append({
                        "Title": recommended_track_name,
                        "Artist": recommended_track_artist,
                        "URL": recommended_track_spotify_url
                        #"ID" : track_id
                    })
    return recommended_track_details

def display_summary(recommended_track_params):

    # Reverse mapping dictionary
    mode_mapping_inv = {1: "Major", 0: "Minor"}
    pitch_class_notation_inv = {
        0: "C", 1: "C♯/D♭", 2: "D", 3: "D♯/E♭", 4: "E", 5: "F",
        6: "F♯/G♭", 7: "G", 8: "G♯/A♭", 9: "A", 10: "A♯/B♭", 11: "B"
    }

    # Exclude size and seeds from summary
    summary_params = {key: value for key, value in recommended_track_params.items() if key not in ['size', 'seeds']}

    for param_name, param_value in summary_params.items():
        # Mode
        if param_name == 'mode':
            display_value = mode_mapping_inv.get(param_value, "Whatever")
            st.write(f"**Mode** : {display_value}")
        
        # Key
        elif param_name == 'key':
            display_value = pitch_class_notation_inv.get(param_value, "Whatever")
            st.write(f"**Key** : {display_value}")
        
        # Other params
        else:
            formatted_name = param_name.replace('_', ' ').title()
            st.write(f"**{formatted_name}** : {param_value}")
        

# Initialize ags for recommendation
seeds = track_ids
recommended_track_params = build_params(seeds)

# # Display summary of selection
# st.header("Summary of your selection", divider = True)
# display_summary(recommended_track_params)

url = "https://api.reccobeats.com/v1/track/recommendation"

# Generate a list a recommended tracks
st.header("Let the magic works :sparkles:", divider = 'green')
left, middle, right = st.columns(3)
if middle.button("Generate my tracks", icon="🎶"):
    recommendation = get_recommendation(url, recommended_track_params)

    # Display the recommended tracks
    
    st.dataframe(recommendation)