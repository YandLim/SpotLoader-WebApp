from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import Database


app = Flask(__name__)
app.secret_key = "Spot"
db = Database()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login", methods=["POST", "GET"])
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
                return redirect(url_for("home"))
        except:
            flash("Couldn't find the email", "info")
            return render_template("login.html")
    else:
        if "email" in session and "password" in session:
            flash("Welcome back", "info")
            return redirect(url_for("home"))
        else:
            return render_template("login.html")
    

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user_email = request.form["email"].lower()
        user_passw = request.form["password"]
        user_name = request.form["name"]
        user_gender = request.form["gender"].upper()
        user_dob = request.form["dob"]

        db.add_user(user_email, user_passw, user_name, user_gender, user_dob)
        return redirect(url_for("home"))
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
