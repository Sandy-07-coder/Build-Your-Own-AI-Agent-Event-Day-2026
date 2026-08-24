import json
import time
import httpx

from ..config import (
    REQUEST_TIMEOUT,
    OPENAI_API_KEY,
    JUDGE_MODEL
)


async def call_agent(webhook, message):

    start = time.perf_counter()

    try:

        async with httpx.AsyncClient(
            timeout=REQUEST_TIMEOUT
        ) as client:

            response = await client.post(
                webhook,
                json={
                    "message": message,
                    "session_id": "event-evaluation"
                }
            )

        latency = (
            time.perf_counter() - start
        ) * 1000

        try:
            data = response.json()
        except Exception:
            data = {
                "response": response.text
            }

        text = extract_response(data)

        return {
            "success": (
                200 <= response.status_code < 300
            ),
            "status_code": response.status_code,
            "response": text,
            "latency": round(latency, 2)
        }

    except Exception as exc:

        return {
            "success": False,
            "status_code": 0,
            "response": "",
            "latency": 0,
            "error": str(exc)
        }


def extract_response(data):

    if isinstance(data, str):
        return data

    if not isinstance(data, dict):
        return str(data)

    for key in [
        "response",
        "output",
        "answer",
        "message",
        "text",
        "result"
    ]:

        if isinstance(data.get(key), str):
            return data[key]

    return str(data)


async def llm_score(
    agent_description,
    problem,
    test_input,
    response
):

    if not OPENAI_API_KEY:

        return heuristic_score(
            problem,
            test_input,
            response
        )

    try:

        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=OPENAI_API_KEY
        )

        prompt = f"""
You are an objective automated competition judge.

Evaluate an AI agent response.

Agent purpose:
{agent_description}

Problem:
{problem}

Test:
{test_input}

Response:
{response}

Give a score from 0 to 5.

5 = excellent
4 = strong
3 = acceptable
2 = weak
1 = very poor
0 = failed

Evaluate:
- relevance
- usefulness
- correctness
- instruction following
- whether the answer fits the stated agent purpose

Return ONLY JSON:

{{
  "score": 0,
  "reason": "short explanation"
}}
"""

        result = await client.chat.completions.create(
            model=JUDGE_MODEL,
            temperature=0,
            response_format={
                "type": "json_object"
            },
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        data = json.loads(
            result.choices[0].message.content
        )

        return {
            "score": max(
                0,
                min(
                    5,
                    float(data.get("score", 0))
                )
            ),
            "reason": data.get(
                "reason",
                ""
            )
        }

    except Exception as exc:

        return {
            "score": 0,
            "reason": str(exc)
        }


def heuristic_score(problem, test, response):

    if not response:
        return {
            "score": 0,
            "reason": "No response received."
        }

    length = len(response.strip())

    if length < 20:
        return {
            "score": 1,
            "reason": "Response is too short."
        }

    if length < 80:
        return {
            "score": 3,
            "reason": "Basic response received."
        }

    return {
        "score": 4,
        "reason": "Valid substantive response received."
    }


def calculate_scores(results):

    if not results:
        return 0, 0, 0, 0

    functional_passes = sum(
        1 for r in results
        if r["success"]
    )

    functionality = (
        functional_passes /
        len(results)
    ) * 100

    quality_values = [
        r["quality"]
        for r in results
    ]

    quality = (
        sum(quality_values) /
        len(quality_values) /
        5
    ) * 100

    robustness_tests = [
        r for r in results
        if r["category"] in [
            "edge_case",
            "out_of_scope",
            "failure_handling"
        ]
    ]

    if robustness_tests:

        robustness = (
            sum(
                1 for r in robustness_tests
                if r["quality"] >= 2
            ) /
            len(robustness_tests)
        ) * 100

    else:
        robustness = functionality

    final = (
        functionality * 0.35 +
        quality * 0.40 +
        robustness * 0.25
    )

    return (
        round(functionality, 2),
        round(quality, 2),
        round(robustness, 2),
        round(final, 2)
    )
