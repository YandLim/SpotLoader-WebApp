from flask import Flask
from config import Config
from routes.users import users_bp
from routes.function import function_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

app.register_blueprint(users_bp)
app.register_blueprint(function_bp)

if __name__ == "__main__":
    app.run(debug=True)
