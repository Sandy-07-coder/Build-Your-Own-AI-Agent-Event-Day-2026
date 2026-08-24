from flask import Blueprint, jsonify

from ..database import get_db

leaderboard = Blueprint(
    "leaderboard",
    __name__
)


@leaderboard.get(
    "/api/leaderboard"
)
def get_leaderboard():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            t.team_name,
            s.agent_name,
            e.functionality,
            e.quality,
            e.robustness,
            e.final_score
        FROM evaluations e
        JOIN submissions s
            ON s.id = e.submission_id
        JOIN teams t
            ON t.id = s.team_id
        ORDER BY e.final_score DESC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])
