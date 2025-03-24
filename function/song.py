from flask import current_app
from requests import post, get
import base64
import json
from dotenv import load_dotenv


class Main:
    # Get the token for authentication
    def get_token(self):
        auth_string = current_app.config["CLIENT_ID"] + ":" + current_app.config["CLIENT_SECRET"]
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


    # Take the song data
    def get_songs(self, token, song_name, limit):
        url = f"https://api.spotify.com/v1/search?q={song_name}r&type=track&limit={limit}&market=US"
        headers = {"Authorization": "Bearer "+ token}
        result = get(url, headers=headers)
        json_result = json.loads(result.content)
        return json_result


    # The main function
    def main(self, result):
        """
        The output format would be 
        songs_data[0]:['song name', '[artists name]', 'song's link', 'album name', 'release data', 'image's link']
        """
        song_data = []

        # Looping throught every found_result
        for i in range(len(result["tracks"]["items"])):
            temp_data = []
            artists = []
            temp_data.append(result["tracks"]["items"][i]["name"]) # Extracting the song's name

            # Looping to extract all the artists's name
            for x in range(len(result["tracks"]["items"][i]["artists"])):
                artists.append(result["tracks"]["items"][i]["artists"][x]["name"])
                
            temp_data.append(artists)

            temp_data.append(result["tracks"]["items"][i]["external_urls"]["spotify"]) # Extracting the song's link
            temp_data.append(result["tracks"]["items"][i]["album"]["name"]) # Extracting the song's album

            # Extracting the song's release date
            release_date = result["tracks"]["items"][i]["album"]["release_date"] 
            if release_date == "0000":
                release_date = None
            temp_data.append(release_date)

            # Extracting the song's image
            try:
                temp_data.append(result["tracks"]["items"][i]["album"]["images"][0]["url"])
            except:
                temp_data.append(None)


            song_data.append(temp_data)
        return song_data

