from flask import Blueprint, session, jsonify

from ..database import get_db
from ..auth.service import team_required

teams = Blueprint("teams", __name__)


@teams.get("/api/team/me")
@team_required
def my_team():

    conn = get_db()

    team = conn.execute(
        "SELECT id, team_name, username, members, active FROM teams WHERE id = ?",
        (session["team_id"],)
    ).fetchone()

    conn.close()

    if not team:
        return jsonify({
            "error": "Team not found"
        }), 404

    data = dict(team)

    return jsonify(data)
