from flask import Blueprint, request, session, jsonify
from werkzeug.security import check_password_hash

from ..database import get_db
from ..config import ADMIN_USERNAME, ADMIN_PASSWORD

auth = Blueprint("auth", __name__)


@auth.post("/api/auth/team-login")
def team_login():

    data = request.json or {}

    username = data.get("username", "").strip()
    password = data.get("password", "")

    conn = get_db()

    team = conn.execute(
        "SELECT * FROM teams WHERE username = ? AND active = 1",
        (username,)
    ).fetchone()

    conn.close()

    if not team:
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    if not check_password_hash(
        team["password_hash"],
        password
    ):
        return jsonify({
            "error": "Invalid credentials"
        }), 401

    session.clear()

    session["role"] = "team"
    session["team_id"] = team["id"]
    session["team_name"] = team["team_name"]

    return jsonify({
        "success": True,
        "team": team["team_name"]
    })


@auth.post("/api/auth/admin-login")
def admin_login():

    data = request.json or {}

    username = data.get("username", "")
    password = data.get("password", "")

    if (
        username != ADMIN_USERNAME
        or password != ADMIN_PASSWORD
    ):
        return jsonify({
            "error": "Invalid admin credentials"
        }), 401

    session.clear()
    session["role"] = "admin"

    return jsonify({
        "success": True
    })


@auth.post("/api/auth/logout")
def logout():

    session.clear()

    return jsonify({
        "success": True
    })


@auth.get("/api/auth/me")
def me():

    return jsonify({
        "role": session.get("role"),
        "team_id": session.get("team_id"),
        "team_name": session.get("team_name")
    })
