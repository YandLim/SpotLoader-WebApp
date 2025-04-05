# Importing the framworks and function from database.py
from flask import render_template, request, redirect, url_for, session, flash, Blueprint
from function.database import Database

# Make Blueprint for current file and call the Database all-in class
users_bp = Blueprint("users", __name__)
db = Database()


# Define home or starting point of web app
@users_bp.route("/")
def home():
    session["destination"] = "Home"
    return render_template("home.html")


# Define login function and route
@users_bp.route("/login", methods=["POST", "GET"])
def login():
    # if user method is post
    if request.method == "POST":
        # Get the user email and password that are inputted
        user_email = request.form["email"].lower()
        user_passw = request.form["password"]

        # Try to match the email
        try:
            # Call the databse function to get the password
            db_user_data = db.call_data("Users", "password", "email", user_email)

            # If the password is match with the data
            if user_passw == db_user_data[0]:
                session.update({
                "email": user_email,
                "password": user_passw,
                })

                # Redirect to the destination url
                flash("Login succesfully", "info")
                if session["destination"] == "search":
                    return redirect(url_for("function.main_page"))
                
                elif session["destination"] == "download":
                    return redirect(url_for("function.song_downloader"))
                
                else:
                    return redirect(url_for("users.home"))
                
            # If the password is not match
            else:
                flash("Wrong password. Please try again")
                return render_template("login.html")
            
        # If the email not matched
        except:
            flash("Couldn't find the email", "info")
            return render_template("login.html")
        
    # if user method is get
    else:
        # Check if user already login and redirect them to destination url
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
    

# Define register route and function
@users_bp.route("/register", methods=["POST", "GET"])
def register():
    # If user method is post
    if request.method == "POST":
        # Get all the user input
        user_email = request.form["email"].lower()
        user_passw = request.form["password"]
        user_name = request.form["name"]
        user_gender = request.form["gender"].upper()
        user_dob = request.form["dob"]

        # Check if email already registered or not
        exist_email = db.call_data("Users", "password", "email", user_email)
        if exist_email is None:
            flash("The email account is been used try login", "info")

        # Registered the user into database
        db.add_user(user_email, user_passw, user_name, user_gender, user_dob)

        session.update({
        "email": user_email,
        "password": user_passw,
        })
        
        return redirect(url_for("users.home"))
    
    # If user method is get
    else:
        # Check if the user already login
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
    

# Define logout function and route
@users_bp.route("/logout/")
def logout():
    # Check if the user already login or not
    if "email" in session and "password" in session:
        # Clear the session
        flash("You've been logging out", "info")
        session.pop("email", None)
        session.pop("password", None)
    else:
        flash("You are not logging in yet")
    return redirect(url_for("users.home"))


# Delete the account
@users_bp.route("/acount_delete", methods=["POST", "GET"])
def delete_account():
    # Try to get the email to check id user already login
    try:
        user_email = session["email"]
    except:
        flash("You are not logging in yet")
        return redirect(url_for("users.home"))
    
    # If user method is post
    if request.method == "POST":
        # Get the needed confirmation text
        user_input = request.form["user-confirmation"]

        # Match the text
        if user_input == session["delete_confirmation"]:
            db.delete_user("email", user_email, "Users") # Delete the account
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