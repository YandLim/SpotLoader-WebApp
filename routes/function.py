from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify, send_file, stream_with_context, Response
from function.song import Main
from function.zipped import zipped
import shutil
import time
import re

function_bp = Blueprint("function", __name__)
max_tried = 3
Fm = Main()
Zp = zipped()


@function_bp.route("/searcher", methods=["POST", "GET"])
def main_page():
    song_names = []
    artists_name = []
    songs_link = []
    albums_name = []
    release_date = []
    image_link = []
    youtube_link = []

    if request.method == "POST":
        entry_song = request.form["song-input"]
        limit = request.form["result-qty"]

        token = Fm.get_token()
        results = Fm.search(Fm.get_songs(token, entry_song, limit))

        for result in results:
            song_names.append(result[0])
            artists_name.append(result[1])
            songs_link.append(result[2])
            albums_name.append(result[3])
            release_date.append(result[4])
            image_link.append(result[5])

        for artist, song in zip(artists_name, song_names):
            yt_link = Fm.search_youtube(f"{song} - {artist}")
            youtube_link.append(yt_link)

        data = zip(song_names, artists_name, songs_link, albums_name, release_date, image_link, youtube_link)
        return render_template("search.html", songs_data=data)
    else:
        if "email" not in session and "password" not in session:
            session["destination"] = "search"
            return redirect(url_for("users.login"))
        return render_template("search.html")


@function_bp.route("/downloader", methods=["POST", "GET"])
def song_downloader():   
    found_song = []
    thumbnail_url = []
    artist_name = []

    if request.method == "POST":
        status = True
        song_link = request.form["link-input"]
        token = Fm.get_token()

        splitting = song_link[8:].split("/")
        user_link = song_link[:8] + "/".join(splitting).split("?")[0]

        try:
            if user_link.split("/")[3] == "album":
                link_type = "album"
                playlist_id = user_link.split("/")[4]
                playlist_songs = Fm.get_album_song(token, playlist_id)

                items = playlist_songs["tracks"]["items"]
                parent_name = playlist_songs["name"]

                for i in range(len(playlist_songs["artists"])):
                    artist_name.append(playlist_songs["artists"][0]["name"])

                # Looping throught every found song
                for song in items:
                    full_title = f"{song["artists"][0]["name"]} - {song['name']}"

                    # Store all founded songs and thumbnails 
                    thumbnail_url.append(playlist_songs["images"][0]["url"])
                    found_song.append(full_title)

            elif user_link.split("/")[3] == "playlist":
                link_type = "playlist"
                playlist_id = user_link.split("/")[4]
                url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
                playlist_songs, next_playlist, parent_name, owner_name, playlist_thumbnail = Fm.get_playlist_song(token, url)
                items = playlist_songs["tracks"]["items"]

                # If song is more than 100, proccesing every 100
                if next_playlist:
                    while next_playlist:
                        playlist_songs, next_playlist = Fm.get_playlist_song(token, next_playlist)
                        items.extend(playlist_songs["items"])
                    for song in items:
                        try:
                            full_title = f"{song["track"]["name"]} - {song["track"]["artists"][0]["name"]}"

                            thumbnail_url.append(song["track"]["album"]["images"][0]["url"])
                            found_song.append(full_title)
                        except:
                            continue
                        
                # If not 100 or less than 100 
                else:
                    for song in items:
                        full_title = f"{song["track"]["name"]} - {song["track"]["artists"][0]["name"]}"

                        thumbnail_url.append(song["track"]["album"]["images"][0]["url"])
                        found_song.append(full_title)

            # If it is individual song
            elif user_link.split("/")[3] == "track":
                link_type = "song"
                song_id = user_link.split("/")[4].split("?")[0]
                song_title, artist_name, thumbnail = Fm.get_a_songs(token, song_id)
                full_title = f"{song_title} - {", ".join(artist_name)}"

                thumbnail_url.append(thumbnail)
                found_song.append(full_title)

        except:
            status = False

        if status == True:
            if link_type == 'album':
                session["found_song"] = found_song
                session["parent_name"] = parent_name
                session["thumbnail_url"] = thumbnail_url
                return render_template("download.html", status="cool", type=link_type, found_song=found_song, album_name=parent_name, artists=artist_name, thumbnail=thumbnail_url[0])
            
            elif link_type == "playlist":
                session["found_song"] = found_song
                session["parent_name"] = parent_name
                session["thumbnail_url"] = thumbnail_url
                return render_template("download.html", status="cool", type=link_type, found_song=found_song, playlist_name=parent_name, owner=owner_name, playlist_thumbnail=playlist_thumbnail)
            
            elif link_type == "song":
                session["found_song"] = [found_song[0]]
                session["parent_name"] = found_song[0]
                session["thumbnail_url"] = [thumbnail_url[0]]
                return render_template("download.html", status="cool", type=link_type, found_song=found_song[0].split("-")[0], artists=artist_name, thumbnail=thumbnail_url[0])
        else:
            print("NO COOL")
            return
    else:
        if "email" not in session and "password" not in session:
            session["destination"] = "download"
            return redirect(url_for("users.login"))
        return render_template("download.html")

@function_bp.route("/run_download", methods=["POST"])
def download_clicked():
    global download_progress
    session_id = session.get("session_id", "default")
    download_progress[session_id] = 0  # Reset progress    sanitize_name = []

    sanitize_name = []
    youtube_links = []
    song_file_name = []
    cover_pic_name = []

    found_song = session["found_song"]
    parent_name = session["parent_name"]
    thumbnail_url = session["thumbnail_url"]

    DOWNLOAD_FOLDER = f"static/downloads/{parent_name}" if len(found_song) > 1 else "static/finish_files"
    PIC_FOLDER = f"static/pic/{parent_name}" if len(found_song) > 1 else "static/downloads/pic"

    session["progress"] = 10
    print("🧹 Cleaning file name")
    for file_name in found_song:
        for _ in range(max_tried):
            try:
                sanitized = re.sub(r'[<>:"/\\|?.*!@#$%^&]', '', file_name)
                sanitize_name.append(sanitized)
                break
            except Exception as e:
                print(f"Error {_}\nRetrying the procces")
    print(sanitize_name)

    session["progress"] = 20
    for song in found_song:
        youtube_link = Fm.search_youtube(song)
        youtube_links.append(youtube_link)
    print(f"🎶 Found {len(youtube_links)} link")
    
    session["progress"] = 50 
    for url, name in zip(youtube_links, sanitize_name):
        for _ in range(max_tried):
            try:                        
                file_name = Fm.download_song(url, name, DOWNLOAD_FOLDER)
                song_file_name.append(file_name)
                break
            except Exception as e:
                print(f"Error ocured:\n{e}\nRetrying the procces")
    print(f"🎉 Success downloading {len(song_file_name)} Songs") 

    session["progress"] = 70
    for i, (url, name) in enumerate(zip(thumbnail_url, sanitize_name)):
        for _ in range(max_tried):
            try:
                cover_name = Fm.get_thumbnail(url, name, PIC_FOLDER)
                cover_pic_name.append(cover_name)
                break
            except Exception as e:
                print(f"Error ocured:\n{e}\nRetrying the procces")
    print("👌 Got'em") 

    session["progress"] = 85  
    for i, (song, cover_pic) in enumerate(zip(song_file_name, cover_pic_name)):
        for _ in range(max_tried):
            try:
                Fm.add_thumbnail(song, cover_pic, DOWNLOAD_FOLDER)
                break
            except:
                continue
    print("🎵 All thumbnails updated successfully!") 

    session["progress"] = 100
    store_path = Zp.create_zip(parent_name, DOWNLOAD_FOLDER) if len(found_song) > 1 else f"static/finish_files/{found_song[0]}.mp3"
    session["zip_path"] = store_path

    if len(found_song) > 1:
        shutil.rmtree(DOWNLOAD_FOLDER)

    shutil.rmtree(PIC_FOLDER)

    return jsonify({
        "message": "Download is ready!",
        "download_url": url_for('static', filename=f'zipped/{parent_name}.zip', _external=True)
    })


@function_bp.route("/download_zip")
def DOWNLOAD():
    zip_path = session["zip_path"]
    session.pop("zip_path", None)
    return send_file(zip_path, as_attachment=True)
