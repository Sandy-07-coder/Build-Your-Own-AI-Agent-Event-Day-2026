from flask import Blueprint, jsonify

from ..database import get_db
from ..auth.service import team_required, admin_required

from evaluator.engine.runner import (
    call_agent,
    llm_score,
    calculate_scores
)

import json

evaluations = Blueprint(
    "evaluations",
    __name__
)


def load_hidden_tests():

    from pathlib import Path

    directory = (
        Path(__file__).resolve()
        .parents[2]
        / "evaluator"
        / "test-cases"
        / "hidden"
    )

    cases = []

    for file in directory.glob("*.json"):

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if isinstance(data, list):
                cases.extend(data)
            else:
                cases.append(data)

    return cases


async def run_evaluation(submission):

    tests = load_hidden_tests()

    results = []

    for test in tests:

        call = await call_agent(
            submission["webhook_url"],
            test["input"]
        )

        quality = 0
        reason = ""

        if call["success"]:

            judged = await llm_score(
                submission["description"],
                submission["problem"],
                test["input"],
                call["response"]
            )

            quality = judged["score"]
            reason = judged["reason"]

        else:

            reason = (
                call.get(
                    "error",
                    "Agent request failed"
                )
            )

        results.append({
            "id": test["id"],
            "category": test["category"],
            "input": test["input"],
            "success": call["success"],
            "quality": quality,
            "latency": call["latency"],
            "response": call["response"],
            "reason": reason
        })

    functionality, quality, robustness, final = (
        calculate_scores(results)
    )

    return {
        "functionality": functionality,
        "quality": quality,
        "robustness": robustness,
        "final_score": final,
        "tests": results
    }


@evaluations.post(
    "/api/evaluations/run/<int:submission_id>"
)
@admin_required
async def run_submission(submission_id):

    conn = get_db()

    submission = conn.execute("""
        SELECT * FROM submissions
        WHERE id = ?
    """, (
        submission_id,
    )).fetchone()

    if not submission:

        conn.close()

        return jsonify({
            "error": "Submission not found"
        }), 404

    result = await run_evaluation(
        dict(submission)
    )

    conn.execute("""
        INSERT INTO evaluations (
            submission_id,
            functionality,
            quality,
            robustness,
            final_score,
            result_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        submission_id,
        result["functionality"],
        result["quality"],
        result["robustness"],
        result["final_score"],
        json.dumps(result)
    ))

    conn.execute("""
        UPDATE submissions
        SET status = 'evaluated'
        WHERE id = ?
    """, (
        submission_id,
    ))

    conn.commit()
    conn.close()

    return jsonify(result)


@evaluations.get(
    "/api/evaluations/mine"
)
@team_required
def team_evaluations():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            e.*,
            s.agent_name
        FROM evaluations e
        JOIN submissions s
            ON s.id = e.submission_id
        WHERE s.team_id = ?
        ORDER BY e.created_at DESC
    """, (
        __import__("flask").session[
            "team_id"
        ],
    )).fetchall()

    conn.close()

    return jsonify([
        dict(row)
        for row in rows
    ])


@evaluations.get(
    "/api/admin/evaluations"
)
@admin_required
def all_evaluations():

    conn = get_db()

    rows = conn.execute("""
        SELECT
            e.*,
            s.agent_name,
            t.team_name
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
