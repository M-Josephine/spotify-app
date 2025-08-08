import spotipy
from spotipy.oauth2 import SpotifyOAuth
#import cred
import streamlit as st
import pandas as pd
import re
import requests
import streamlit.components.v1 as components


# Main script
############################### Header ########################################

st.title("Pimp my track :sunglasses:")
st.write('The recommended track will be generated based on your Spotify top tracks, as well as song attributes such as danceability or popularity, that you will be able to tune a little further.')

############################### GET TOP TRACKS ########################################

# Get user top tracks

# Authenticate to Spotify API
def api_spotify_auth(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=st.secrets.spotify_api_credentials.client_id, client_secret= st.secrets.spotify_api_credentials.client_secret, redirect_uri=st.secrets.spotify_api_credentials.redirect_url, scope=scope))
    return sp

# Get 5 top tracks
def get_top_tracks(time_range, track_nb, offset, sp):

    # API response
    top_tracks = sp.current_user_top_tracks(limit=track_nb, offset=offset, time_range=time_range)
    
    # Create dataframe and list of ids
    track_details = []
    track_number = len(top_tracks["items"])
    track_ids = []
    #print(track_number)

    for i in range(track_number):
        track_name = top_tracks['items'][i]['name']
        track_artists = top_tracks['items'][i]['artists'][0]['name']
        track_id = top_tracks['items'][i]['id']
        

        track_details.append({
                    "Title": track_name,
                    "Artist": track_artists,
                    "ID" : track_id
                })
        
        track_ids.append(track_id)
        

    df_tracks = pd.DataFrame(track_details)
    
    # Display the track details
    # st.dataframe(df_tracks, hide_index=True)

    # Display the top tracks. As we want to display the player, we can't use st.dataframe here
    #col1, col2, col3 = st.columns([0.3, 0.3, 0.8])
    #col1.markdown("**Title**")
    #col2.markdown("**Artist**")
    st.markdown("**Your top tracks**")
    
    for index, row in df_tracks.iterrows():
        # col1, col2, col3 = st.columns([0.3, 0.3, 0.8])
        # col1.markdown(row['Title'])
        # col2.markdown(row['Artist'])
        
        embed_code = f"""
            <iframe src="https://open.spotify.com/embed/track/{row['ID']}" width="100%" height="80" 
                    frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
        """
        #with col3:
        components.html(embed_code, height=100)
    
    return track_ids


############################### RECOMMENDATION ########################################
# Reccobeats 
# Get recommendations

def build_params(seeds):
    
    # Define param for each feature with widgets
    # Features with values of 0 to 1
    st.header("Now, tune it your way", divider = 'green')
    enable_sliders = st.toggle("Select track features")
    if enable_sliders:
        st.markdown('Acousticness',help = "Acousticness refers to how much of a song or piece of music is made up of natural, organic sounds rather than synthetic or electronic elements. In other words, it's a measure of how 'acoustic' a piece of music sounds. A confidence measure from 0.0 to 1.0, greater value represents higher confidence the track is acoustic.")
        acousticness = st.slider("Acousticness :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Danceability',help = "Danceability is a measure of how suitable a song is for dancing, ranging from 0 to 1. A score of 0 means the song is not danceable at all, while a score of 1 indicates it is highly danceable. This score takes into account factors like tempo, rhythm, beat consistency, and energy, with higher scores indicating stronger, more rhythmically engaging tracks.")
        danceability = st.slider("Danceability :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Energy',help ="Energy in music refers to the intensity and liveliness of a track, with a range from 0 to 1. A score of 0 indicates a very calm, relaxed, or low-energy song, while a score of 1 represents a high-energy, intense track. It’s influenced by elements like tempo, loudness, and the overall drive or excitement in the music.")
        energy = st.slider("Energy :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Instrumentalness',help ="Predicts whether a track contains no vocals. “Ooh” and “aah” sounds are treated as instrumental in this context. Rap or spoken word tracks are clearly “vocal”. The closer the instrumentalness value is to 1.0, the greater likelihood the track contains no vocal content. Values above 0.5 are intended to represent instrumental tracks, but confidence is higher as the value approaches 1.0.")
        instrumentalness = st.slider("Instrumentalness :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Liveness',help ="Detects the presence of an audience in the recording. Higher liveness values represent an increased probability that the track was performed live. A value above 0.8 provides strong likelihood that the track is live.")
        liveness = st.slider("Liveness :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Speechiness',help ="Speechiness detects the presence of spoken words in a track. The more exclusively speech-like the recording (e.g. talk show, audio book, poetry), the closer to 1.0 the attribute value. Values above 0.66 describe tracks that are probably made entirely of spoken words. Values between 0.33 and 0.66 describe tracks that may contain both music and speech, either in sections or layered, including such cases as rap music. Values below 0.33 most likely represent music and other non-speech-like tracks.")
        speechiness = st.slider("Speechiness :", 0.0, 1.0, 0.2, label_visibility = "hidden")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('Valence',help ="Valence in music measures the emotional tone or mood of a track, with a range from 0 to 1. A score of 0 indicates a song with a more negative, sad, or dark feeling, while a score of 1 represents a more positive, happy, or uplifting mood. Tracks with a high valence tend to feel joyful or energetic, while those with a low valence may evoke feelings of melancholy or sadness.")
        valence = st.slider("Valence :", 0.0, 1.0, 0.2, label_visibility = "hidden")
    else:
        acousticness = None
        danceability = None
        energy = None
        instrumentalness = None
        liveness = None
        speechiness = None
        valence = None

    # Mode can be 1 (Major) or 0 (Minor)
    options = ["Whatever", "Major", "Minor" ]
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('Mode',help = "Mode indicates the modality (major or minor) of a track.")
    mode = st.pills("Mode", options, label_visibility = "hidden")
    mode_mapping ={
        "Whatever": None,
        "Major": 1,
        "Minor":0
    }
    mode = mode_mapping.get(mode)

    # Key can be -1 to 11 according pitch class notation
    options = ["Whatever","C", "C♯/D♭", "D", "D♯/E♭", "E", "F", "F♯/G♭", "G", "G♯/A♭", "A", "A♯/B♭", "B"]
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('Key',help = "The key the track is in.")
    key = st.pills("Key", options, label_visibility = "hidden")
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

    # Tempo can be 0 to 250 (BPM)
    st.markdown("<br>", unsafe_allow_html=True)
    enable_tempo = st.toggle("Select track tempo")
    if enable_tempo:
        st.markdown('Tempo (bpm)',help = "Estimated tempo in beats per minute (BPM).")
        tempo = st.slider("Tempo (bpm) :", 1, 250, 1, label_visibility = "hidden")
    else:
        tempo = None

    # Popularity can be 0 to 100
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('Popularity',help = "The popularity of the track. The value will be between 0 and 100, with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are. Generally speaking, songs that are being played a lot now will have a higher popularity than songs that were played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated independently. Artist and album popularity is derived mathematically from track popularity. Note: the popularity value may lag actual popularity by a few days: the value is not updated in real time.")
    popularity = st.slider("Popularity:", 1, 100, 1, label_visibility = "hidden")

    # Size is the number of tracks: can be 1 to 100
    # size = st.number_input("Insert a number of track", min_value = 1, max_value = 100)
    size = 1

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
    # Get API response Reccobeats
    response = requests.get(url, params=recommended_track_params)
    recommended_track = response.json()
    
    recommended_track_number = len(recommended_track["content"])

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

    # Reverse mapping dictionary to get the labels associated to the int for mode and key
    mode_mapping_inv = {1: "Major", 0: "Minor"}
    pitch_class_notation_inv = {
        0: "C", 1: "C♯/D♭", 2: "D", 3: "D♯/E♭", 4: "E", 5: "F",
        6: "F♯/G♭", 7: "G", 8: "G♯/A♭", 9: "A", 10: "A♯/B♭", 11: "B"
    }

    # Create dictionary with key/value, eExclude size and seeds from summary
    summary_params = {key: value for key, value in recommended_track_params.items() if key not in ['size', 'seeds']}

    # Display the summary
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
        

############################### Save tracks to user's liked songs playlist ########################################


# Save track for current user (to liked song playlist)
# Not needed as the player has a feature to save the track
# def save_track_to_liked_songs(recommendation):

#     # Authenticate to API with the appropriate scope
#     sp = api_spotify_auth("user-library-modify")

#     # Retrieve Ids from Spotify URLS in recommendation dico
#     recommended_track_spotify_id = []
#     track_number = len(recommendation)
#     for i in range(track_number):
#         track_spotify_URL = recommendation[i]['URL']
#         track_spotify_id = re.split("/", track_spotify_URL)[-1]
#         recommended_track_spotify_id.append(track_spotify_id)

#     response = sp.current_user_saved_tracks_add(tracks=recommended_track_spotify_id)
#     return response

# Play and save the track
def play_track(recommendation):
    track_number = len(recommendation)
    for i in range(track_number):
        track_spotify_URL = recommendation[i]['URL']
        # Retrieve Id from Spotify URL
        track_spotify_id = re.split("/", track_spotify_URL)[-1]
        track_embed_code = f"""
            <iframe style="border-radius:12px" 
                    src="https://open.spotify.com/embed/track/{track_spotify_id}" 
                    width="100%" height="352" 
                    frameBorder="0" allowfullscreen="" 
                    allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                    loading="lazy"></iframe>
            """
    
        # Display player
        components.html(track_embed_code, height=352)


############################### RUN GET TOP TRACKS + RECOMMENDATION + PLAYER ########################################

st.header("Let's get your Spotify top tracks", divider = 'green')
# widget to choose between long / medium / short term

st.markdown('Spotify time range',help = "Over what time frame the affinities are computed. Valid values: long_term (calculated from ~1 year of data and including all new data as it becomes available), medium_term (approximately last 6 months), short_term (approximately last 4 weeks). Default: medium_term.")

# Define args for get_top_tracks function

time_range_widget= st.pills("Spotify time range", ['Over the last 4 weeks', 'Over the last 6 months', 'Over last year'], label_visibility = "hidden")
time_range_mapping = {
    "Over last year" : "long_term",
    "Over the last 6 months" : "medium_term",
    "Over the last 4 weeks" : "short_term"
}

time_range= time_range_mapping.get(time_range_widget)
track_nb = 5
offset = 0
scope = "user-top-read"

# Auth Spotify API
sp = api_spotify_auth(scope)

# Retrive 5 top tracks IDs (and display in dataframe)
st.markdown("<br>", unsafe_allow_html=True)
track_ids = get_top_tracks(time_range, track_nb, offset, sp)


# Initialize ags for recommendation
seeds = track_ids
# Build params
recommended_track_params = build_params(seeds)

# Entry points in Reccobeats API
url = "https://api.reccobeats.com/v1/track/recommendation"

# Display summary of selection
st.header("Summary of your selection", divider = "green")
display_summary(recommended_track_params)

# Generate a list a recommended tracks with Reccobeats API
st.header("Let the magic works :sparkles:", divider = 'green')
left, middle, right = st.columns(3)
recommendation = get_recommendation(url, recommended_track_params)

if middle.button("Generate my track", icon="🎶"):
    
    # Display the recommended tracks
    st.dataframe(recommendation, hide_index=True)

    # Display players
    play_track(recommendation)

#Save tracks (not needed anymore beacuse included in play_track function)
# left, middle, right = st.columns(3)
# if middle.button("Save it to my Playlist", icon="💾"):
    
#     #Save tracks
#     saving_track = save_track_to_liked_songs(recommendation)

#     # Post successful
#     if saving_track == None:
#         st.write("Your track have been saved! 🎉")