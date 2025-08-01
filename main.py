from flask import Flask, render_template, url_for
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/spotlight')
def artist_spotlight():
    return render_template("artist-spotlight.html")

if __name__ == "__main__":
    app.run(debug=True)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token
    
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query 
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
 
    if len(json_result) == 0:
        print("No artist found")
        return None
    return json_result[0]

def get_all_albums(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def get_album_tracks(token, album_id):
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["items"]
    return json_result

def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

def get_tracks_popularity(token, track_ids):
    try:
        url = f"https://api.spotify.com/v1/tracks?ids={','.join(track_ids)}"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = json.loads(result.content)["tracks"]
        return json_result
    except Exception as e:
            print(f"Error fetching track data: {e}")
            return []


# Main
artist_name = input("Enter an artist ")

limit = -1
while(limit <= 0):
    try:
        limit = int(input("Enter the number of top songs to display:"))
        if limit <= 0:
            print("Don't be stupid, put a postive number :|") 
    except ValueError:
        print(f"Nahhh you're cooked, don't you know what a NUMBER is!")

token = get_token()
result = search_for_artist(token, artist_name)

if result is None:
    print("Artist not found. Blame spotify not me lol")
else:
    if artist_name.lower() == "taylor swift" or artist_name.lower() == "sabrina carpenter":
        print("I can tell you don't season your chicken :(")
    artist_id = result["id"]
    all_albums = get_all_albums(token, artist_id)

    track_ids = []

    for album in all_albums:
        album_tracks = get_album_tracks(token, album["id"])
        for track in album_tracks:
            track_ids.append(track["id"])

    track_id_chunks = list(chunk_list(track_ids, 50))
    all_track_data = []

    for chunk in track_id_chunks:
        tracks_info = get_tracks_popularity(token, chunk)
        for track in tracks_info:
            all_track_data.append({
                "name": track["name"],
                "id": track["id"],
                "popularity": track["popularity"]
            })
    sorted_tracks = sorted(all_track_data, key=lambda x: x['popularity'], reverse=True)

    for idx, track in enumerate(sorted_tracks[:limit]):
        print(f"{idx + 1}. {track['name']} - Popularity: {track['popularity']}")