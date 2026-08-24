from flask import Blueprint, jsonify, request

from ..database import (
    get_db,
    create_team
)

from ..auth.service import admin_required

admin = Blueprint(
    "admin",
    __name__
)


@admin.get(
    "/api/admin/teams"
)
@admin_required
def teams():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            id,
            team_name,
            username,
            members,
            active,
            created_at
        FROM teams
        ORDER BY id
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


@admin.post(
    "/api/admin/teams"
)
@admin_required
def create():

    data = request.json or {}

    success = create_team(
        data.get("team_name"),
        data.get("username"),
        data.get("password"),
        data.get("members", [])
    )

    if not success:

        return jsonify({
            "error": "Username already exists"
        }), 400

    return jsonify({
        "success": True
    })


@admin.get(
    "/api/admin/submissions"
)
@admin_required
def submissions():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            s.*,
            t.team_name,
            e.final_score
        FROM submissions s
        JOIN teams t
            ON t.id = s.team_id
        LEFT JOIN evaluations e
            ON e.submission_id = s.id
        ORDER BY s.created_at DESC
    """).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])
