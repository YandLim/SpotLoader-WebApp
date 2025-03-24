from flask import current_app, render_template, request, redirect, url_for, session, Blueprint
from function.song import Main

function_bp = Blueprint("function", __name__)
Fm = Main()

@function_bp.route("/")
def home():
    return render_template("home.html")


@function_bp.route("/searcher", methods=["POST", "GET"])
def main_page():
    song_names = []
    artists_name = []
    songs_link = []
    albums_name = []
    release_date = []
    image_link = []

    if request.method == "POST":
        entry_song = request.form["song-input"]
        limit = request.form["result-qty"]

        token = Fm.get_token()        
        results = Fm.main(Fm.get_songs(token, entry_song, limit))
        
        for result in results:
            song_names.append(result[0])
            artists_name.append(result[1])
            songs_link.append(result[2])
            albums_name.append(result[3])
            release_date.append(result[4])
            image_link.append(result[5])

        data = zip(song_names, artists_name, songs_link, albums_name, release_date, image_link)
        return render_template("search.html", songs_data=data)
    else:
        if "email" not in session and "password" not in session:
            return redirect(url_for("login"))
        return render_template("search.html")
