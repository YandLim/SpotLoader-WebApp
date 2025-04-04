from flask import render_template, request, redirect, url_for, session, Blueprint, jsonify, send_file, stream_with_context, Response, copy_current_request_context
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


download_progress = {}  # Dictionary global untuk progress
zip_paths = {}  # Dictionary global untuk menyimpan lokasi ZIP'
current_status_progress = {}

@function_bp.route("/run_download", methods=["POST"])
def download_clicked():
    global download_progress, zip_paths, current_status_progress
    session_id = session.get("session_id", "default")
    progres_status = session.get("current_status", "Starting . . . ")

    download_progress[session_id] = 0  # Reset progress
    current_status_progress[progres_status] = "Starting"

    sanitize_name = []
    youtube_links = []
    song_file_name = []
    cover_pic_name = []

    found_song = session.get("found_song", [])
    parent_name = session.get("parent_name", "default")
    thumbnail_url = session.get("thumbnail_url", [])

    DOWNLOAD_FOLDER = f"static/downloads/{parent_name}" if len(found_song) > 1 else "static/finish_files"
    PIC_FOLDER = f"static/pic/{parent_name}" if len(found_song) > 1 else "static/downloads/pic"


    current_progress = 5
    download_progress[session_id] = current_progress
    cleaning_progress = 10 / len(found_song)
    current_status_progress[progres_status] = "🧹 Cleaning file name"
    for file_name in found_song:
        sanitized = re.sub(r'[<>:"/\\|?.*!@#$%^&]', '', file_name)
        sanitize_name.append(sanitized)

        current_progress += cleaning_progress
        download_progress[session_id] = round(current_progress)
    current_status_progress[progres_status] = "✨ Name clean"


    download_progress[session_id] = 15
    youtube_link_progress = 10 / len(found_song)
    current_status_progress[progres_status] = "🔎 Looking for the song in YouTube"
    for song in found_song:
        youtube_link = Fm.search_youtube(song)
        youtube_links.append(youtube_link)

        current_progress += youtube_link_progress
        download_progress[session_id] = round(current_progress)
    current_status_progress[progres_status] = f"🎶 Found {len(youtube_links)} links"


    download_progress[session_id] = 25
    downloads_progress = 45 / len(found_song)
    current_status_progress[progres_status] = "🗂️Downloading the songs"
    for url, name in zip(youtube_links, sanitize_name):
        file_name = Fm.download_song(url, name, DOWNLOAD_FOLDER)
        song_file_name.append(file_name)

        current_progress += downloads_progress
        download_progress[session_id] = round(current_progress)
    current_status_progress[progres_status] = f"🎉 Successfully downloaded {len(song_file_name)} Songs"


    download_progress[session_id] = 70
    download_thumbnail_progress = 10 / len(found_song)
    current_status_progress[progres_status] = "🖼️Downloading the thumbnail"
    for url, name in zip(thumbnail_url, sanitize_name):
        cover_name = Fm.get_thumbnail(url, name, PIC_FOLDER)
        cover_pic_name.append(cover_name)

        current_progress += download_thumbnail_progress
        download_progress[session_id] = round(current_progress)
    current_status_progress[progres_status] = "👌 Got'em"


    download_progress[session_id] = 80
    changing_thumbnail_progress = 10 / len(found_song)
    current_status_progress[progres_status] = "🎨 Changing the song's thumbnail"
    for song, cover_pic in zip(song_file_name, cover_pic_name):
        Fm.add_thumbnail(song, cover_pic, DOWNLOAD_FOLDER)

        current_progress += changing_thumbnail_progress
        download_progress[session_id] = round(current_progress)
    current_status_progress[progres_status] = "🎵 All thumbnails updated successfully!"


    download_progress[session_id] = 95
    store_path = Zp.create_zip(parent_name, DOWNLOAD_FOLDER) if len(found_song) > 1 else f"static/finish_files/{found_song[0]}.mp3"
    zip_paths[session_id] = store_path  # Simpan path ZIP di dictionary


    if len(found_song) > 1:
        shutil.rmtree(DOWNLOAD_FOLDER)
    shutil.rmtree(PIC_FOLDER)
    download_progress[session_id] = 100

    return jsonify({
        "message": "Download is ready!",
        "download_url": url_for('function.DOWNLOAD', _external=True)
    })


@function_bp.route("/download_zip")
def DOWNLOAD():
    session_id = session.get("session_id", "default")
    zip_path = zip_paths.get(session_id)

    if not zip_path:
        return jsonify({"error": "File not found"}), 404

    return send_file(zip_path, as_attachment=True)


@function_bp.route("/download_progress")
def download_progress_event():
    session_id = session.get("session_id", "default")  # Ambil session_id di awal
    progres_status = session.get("current_status", "Starting . . . ")

    @copy_current_request_context  # ⬅ FIX: Copy request context ke function ini
    def generate():
        while True:
            progress = download_progress.get(session_id, 0)
            current_status = current_status_progress.get((progres_status), "Starting...")  # ⬅ Status proses
            yield f"data: {progress}|{current_status}\n\n"
            time.sleep(1)  # Update setiap 1 detik
    return Response(generate(), mimetype="text/event-stream")