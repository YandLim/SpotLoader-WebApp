# Importing libraries
from dotenv import load_dotenv
from requests import post, get
from yt_dlp import YoutubeDL
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, ID3NoHeaderError
import urllib.request
import urllib.parse
import requests
import base64
import json
import os
import re

# Make the backend class
class Main:
    def __init__(self):
        # Load the env data
        load_dotenv()
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")

    # Get the token for authentication
    def get_token(self):
        auth_string = self.client_id + ":" + self.client_secret
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

    # Take the song from album
    def get_album_song(self, token, album_id):
        url = f"https://api.spotify.com/v1/albums/{album_id}"
        headers = {"Authorization": "Bearer "+ token}
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result


    # Take the song from playlist
    def get_playlist_song(self, token, url):
        url = url
        headers = {"Authorization": "Bearer "+ token}
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        next_items = json_result["next"]
        return json_result, next_items


    # Take the an individual song 
    def get_songs(self, token, song_id):
        url = f"https://api.spotify.com/v1/tracks/{song_id}"
        headers = {"Authorization": "Bearer "+ token}
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result


    # Finding song in YouTube using name
    def search_youtube(self, song):
        # Find t=in youtube using name
        search_query = urllib.parse.quote(song)
        url = f"https://www.youtube.com/results?search_query={search_query}"
        
        # Find the videos id and turn into link then store them into found_link
        try:
            html = urllib.request.urlopen(url).read().decode()
            video_ids = re.findall(r"watch\?v=(\S{11})", html)
            if video_ids:
                found_link = f"https://www.youtube.com/watch?v={video_ids[0]}"  # Take the first video found
        
        # Error occured
        except Exception as e:
            return

        return found_link


    # Function to download song from youtube to mp3
    def download_song(self, url, name, DOWNLOAD_FOLDER):
        save_path = os.path.join(DOWNLOAD_FOLDER, name)

        ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': save_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': r'ffmpeg_apk\bin',
        'noplaylist': True
        }

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
            

        except Exception as e:
            return

        store_name = name + ".mp3"

        return store_name


    # Function to remove unacceptable symbol in name such as '?'
    def sanitize_filename(self, name):
        sanitized = re.sub(r'[<>:"/\\|?.*!@#$%^&]', '', name)
        return sanitized


    # Make the needed variabels
    def get_thumbnail(self, url, raw_name, PIC_FOLDER):
        counter = 1
        raw_name = raw_name.split("-")[1]
        name = os.path.join(PIC_FOLDER, f"{raw_name}.jpg")
        response = requests.get(url)

        if os.path.exists(name):  # Cek apakah file sudah ada
            name = name.split(".")[0] + f"{counter}" + ".jpg" # Tambah angka sebelum ekstensi
            counter += 1

        if response.status_code == 200:
            with open(name, "wb") as f:
                f.write(response.content)
        else:
            return

        return name
                

    # Change the songs cover
    def add_thumbnail(self, song, cover_pic, DOWNLOAD_FOLDER):
            song_path = os.path.join(DOWNLOAD_FOLDER, song)  # Merge path using os.path.join

            try:
                audio = MP3(song_path, ID3=ID3)
            except ID3NoHeaderError:  # If the song doesn't have ID3 tag
                audio = MP3(song_path)
                audio.add_tags()

            with open(cover_pic, "rb") as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime="image/jpeg",  # Picture format inculude jpg
                    type=3,
                    desc="Cover",
                    data=img.read()
                ))

            audio.save()  # Save for each changes