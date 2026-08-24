from flask import Blueprint, request, session, jsonify

from ..database import get_db
from ..auth.service import team_required

submissions = Blueprint(
    "submissions",
    __name__
)


@submissions.post("/api/submissions")
@team_required
def create_submission():

    data = request.json or {}

    required = [
        "agent_name",
        "problem",
        "description",
        "webhook_url"
    ]

    for field in required:
        if not data.get(field):
            return jsonify({
                "error": f"{field} is required"
            }), 400

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO submissions (
            team_id,
            agent_name,
            problem,
            description,
            webhook_url,
            tools,
            workflow_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        session["team_id"],
        data["agent_name"],
        data["problem"],
        data["description"],
        data["webhook_url"],
        data.get("tools", ""),
        data.get("workflow_json", "")
    ))

    submission_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "submission_id": submission_id
    })


@submissions.get("/api/submissions/mine")
@team_required
def my_submissions():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            s.*,
            e.functionality,
            e.quality,
            e.robustness,
            e.final_score
        FROM submissions s
        LEFT JOIN evaluations e
            ON e.submission_id = s.id
        WHERE s.team_id = ?
        ORDER BY s.created_at DESC
    """, (
        session["team_id"],
    )).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])
