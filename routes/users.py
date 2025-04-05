from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from function.database import Database

users_bp = Blueprint("users", __name__)
db = Database()


@users_bp.route("/")
def home():
    session["destination"] = "Home"
    return render_template("home.html")


@users_bp.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user_email = request.form["email"].lower()
        user_passw = request.form["password"]
        try:
            db_user_data = db.call_data("Users", "password", "email", user_email)
            if user_passw == db_user_data[0]:
                session.update({
                "email": user_email,
                "password": user_passw,
                })

                flash("Login succesfully", "info")
                if session["destination"] == "search":
                    return redirect(url_for("function.main_page"))
                
                elif session["destination"] == "download":
                    return redirect(url_for("function.song_downloader"))
                
                else:
                    return redirect(url_for("users.home"))
            else:
                flash("Wrong password. Please try again")
                return render_template("login.html")
        except:
            flash("Couldn't find the email", "info")
            return render_template("login.html")
    else:
        if "email" in session and "password" in session:
            flash("Welcome back", "info")
            if session["destination"] == "search":
                return redirect(url_for("function.main_page"))
            
            elif session["destination"] == "download":
                return redirect(url_for("function.song_downloader"))
            
            else:
                return redirect(url_for("users.home"))
        else:
            return render_template("login.html")
    

@users_bp.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_email = request.form["email"].lower()
        user_passw = request.form["password"]
        user_name = request.form["name"]
        user_gender = request.form["gender"].upper()
        user_dob = request.form["dob"]

        exist_email = db.call_data("Users", "password", "email", user_email)
        if exist_email is None:
            flash("The email account is been used try login", "info")

        db.add_user(user_email, user_passw, user_name, user_gender, user_dob)

        session.update({
        "email": user_email,
        "password": user_passw,
        })
        
        return redirect(url_for("users.home"))
    else:
        if "email" in session and "password" in session:
            flash("Welcome back", "info")
            if session["destination"] == "search":
                return redirect(url_for("function.main_page"))
            
            elif session["destination"] == "download":
                return redirect(url_for("function.song_downloader"))
            
            else:
                return redirect(url_for("users.home"))
        else:
            return render_template("register.html")
    

@users_bp.route("/logout/")
def logout():
    if "email" in session and "password" in session:
        flash("You've been logging out", "info")
        session.pop("email", None)
        session.pop("password", None)
    else:
        flash("You are not logging in yet")
    return redirect(url_for("users.home"))


@users_bp.route("/acount_delete", methods=["POST", "GET"])
def delete_account():
    try:
        user_email = session["email"]
    except:
        flash("You are not logging in yet")
        return redirect(url_for("users.home"))
    
    if request.method == "POST":
        user_input = request.form["user-confirmation"]
        if user_input == session["delete_confirmation"]:
            db.delete_user("email", user_email, "Users")
            session.pop("email", None)
            session.pop("password", None)
            return render_template("delete_account.html", delete="DONE")
        else:
            flash("Please input the right sentence to confirm")
            user_name = db.call_data("Users", "name", "email", user_email)
            session["delete_confirmation"] = f"DELETE {user_name[0].upper()} {user_email.upper()}"
            return render_template("delete_account.html", email=user_email.upper(), user_name=user_name[0].upper())
    
    else:
        if "email" in session and "password" in session:
            user_name = db.call_data("Users", "name", "email", user_email)
            session["delete_confirmation"] = f"DELETE {user_name[0].upper()} {user_email.upper()}"
            return render_template("delete_account.html", email=user_email.upper(), user_name=user_name[0].upper())
        else:
            flash("You are not logging in yet", "info")
            return redirect(url_for("users.home"))