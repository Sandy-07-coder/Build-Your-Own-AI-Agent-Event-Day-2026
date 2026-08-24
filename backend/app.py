from flask import Flask, send_from_directory
from flask_cors import CORS

from .config import SECRET_KEY
from .database import init_db

from .auth.routes import auth
from .teams.routes import teams
from .submissions.routes import submissions
from .evaluations.routes import evaluations
from .leaderboard.routes import leaderboard
from .admin.routes import admin

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"


def create_app():

    app = Flask(__name__)

    app.secret_key = SECRET_KEY

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    CORS(
        app,
        supports_credentials=True
    )

    init_db()

    app.register_blueprint(auth)
    app.register_blueprint(teams)
    app.register_blueprint(submissions)
    app.register_blueprint(evaluations)
    app.register_blueprint(leaderboard)
    app.register_blueprint(admin)

    @app.get("/")
    def home():
        return send_from_directory(
            FRONTEND / "team",
            "login.html"
        )

    @app.get("/team/<path:filename>")
    def team_files(filename):
        return send_from_directory(
            FRONTEND / "team",
            filename
        )

    @app.get("/admin/<path:filename>")
    def admin_files(filename):
        return send_from_directory(
            FRONTEND / "admin",
            filename
        )

    @app.get("/shared/<path:filename>")
    def shared_files(filename):
        return send_from_directory(
            FRONTEND / "shared",
            filename
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000,
        debug=True
    )
