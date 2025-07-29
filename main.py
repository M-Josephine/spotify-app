import spotipy
from spotipy.oauth2 import SpotifyOAuth
import cred
import streamlit as st


scope = "user-read-recently-played"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cred.client_id, client_secret= cred.client_secret, redirect_uri=cred.redirect_url, scope=scope))

# results = sp.current_user_recently_played()
# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'], " – ", track['name'])

album_url = st.text_input(label="Please input the album's url:")
st.write(type(album_url))

try:
    type(album_url) is str
except:
    st.error('You need to enter a url')
    st.stop()

   

#album = sp.album('https://open.spotify.com/album/3ly9T2L4pqTZijFgQssd3x?si=TliI5-L5TkK9AFGwOZtaQw')
album = sp.album(album_url)
album_upc = album['external_ids']['upc']
album_artist = album['artists'][0]['name']
album_title = album['name']
album_track_number = album['total_tracks']
st.write(album_upc,'-',album_artist,'-', album_title, '-', album_track_number)

# for idx, item in enumerate(album['tracks']):

# dict_keys(['album_group', 'album_type', 'artists', 'available_markets', 'copyrights', 'external_ids', 'external_urls', 'genres', 'href', 'id', 'images', 'is_playable', 'label', 'name', 'popularity', 'release_date', 'release_date_precision', 'total_tracks', 'tracks', 'type', 'uri'])
# track_number = album['tracks']['items'][i]['track_number']
# track_name = album['tracks']['items'][i]['name']
# track_artists = album['tracks']['items'][i]['artists'][0]['name']
# track_url = album['tracks']['items'][i]['external_urls']['spotify']

for i in range(album_track_number):
    track_number = album['tracks']['items'][i]['track_number']
    track_name = album['tracks']['items'][i]['name']
    track_artists = album['tracks']['items'][i]['artists'][0]['name']
    track_url = album['tracks']['items'][i]['external_urls']['spotify']
    st.write(track_number, '-', track_name, '-', track_artists, '-', track_url)
 
