#!/usr/bin/env python3
"""TD 2 and TD 3: read the decisions of a routing rule, then adapt it to your own.

Synthetic availability scenarios on our TD 1 portfolio models, no API call, no key.

Envelope for unit request cost comparison: 1k input tokens + 1k output tokens
from Groq Developer pricing (2026-10-21), while Free / :free routes have cash = 0.0.
Capability levels (1/2/3) reflect exact TD 1 family reliability on our 20-question batch:
  - Level 1: 100% on period & product list (Cohere :free, Dots :free)
  - Level 2: 100% on age at the order & combinations (gpt-oss-20b)
  - Level 3: 100% on completed age at a date + period/product/age-order (gpt-oss-120b)
"""
import argparse
import json

# Portfolio resources ordered by cost and proven TD 1 capability
RESOURCES = [
    {
        "id": "openrouter:cohere/north-mini-code:free",
        "level": 1,
        "access": "free",
        "available": True,
        "cash": 0.0,
        "allocation": 0.0,
        "reset_minutes": None,
    },
    {
        "id": "openrouter:dots-studio/dots-3-note-preview:free",
        "level": 1,
        "access": "free",
        "available": True,
        "cash": 0.0,
        "allocation": 0.0,
        "reset_minutes": None,
    },
    {
        "id": "groq:openai/gpt-oss-20b",
        "level": 2,
        "access": "subscription",  # Groq Free quota in TD 1 (paid Developer fallback: $0.075/$0.30 per 1M)
        "available": True,
        "cash": 0.0,
        "allocation": 0.000375,  # implicit envelope value (1k in + 1k out)
        "reset_minutes": None,
    },
    {
        "id": "groq:openai/gpt-oss-120b",
        "level": 3,
        "access": "subscription",  # Groq Free quota in TD 1 (paid Developer fallback: $0.15/$0.60 per 1M)
        "available": True,
        "cash": 0.0,
        "allocation": 0.00075,
        "reset_minutes": None,
    },
    {
        "id": "groq:openai/gpt-oss-120b:developer-paid",
        "level": 3,
        "access": "tokens",
        "available": True,
        "cash": 0.00075,  # $0.15/1M in + $0.60/1M out for 1k+1k tokens
        "allocation": 0.00075,
        "reset_minutes": None,
    },
]


def choose(request, resources):
    """Deterministic routing policy justified by TD 1 family accuracy and portfolio prices."""
    difficulty = request["difficulty"]
    eligible = [r for r in resources if r["level"] >= difficulty]

    if request["high_impact"]:
        checks = "2-of-3 quorum (or dual OSS check on age/combinations) + reference/human review"
    elif difficulty >= 2:
        checks = "SQL date/age boundary check + read-only sandbox execution"
    else:
        checks = "read-only sandbox execution and non-null value check"

    # 1. Prefer available zero-cash routes (OpenRouter :free or Groq Free quota)
    included = [r for r in eligible if r["available"] and r["cash"] == 0]
    if included:
        chosen = min(included, key=lambda r: (r["allocation"], r["level"], r["id"]))
        return {
            "action": "run",
            "resource": chosen["id"],
            "cash": 0.0,
            "checks": checks,
            "reason": (
                f"cheapest available zero-cash route with TD 1 capability level {chosen['level']} "
                f"for difficulty {difficulty}"
            ),
        }

    # 2. Defer if request can wait and a zero-cash eligible quota resets before deadline
    waiting = [
        r for r in eligible
        if not r["available"] and r["cash"] == 0
        and r["reset_minutes"] is not None
        and 0 < r["reset_minutes"] <= request["deadline_minutes"]
    ]
    if waiting and request["can_wait"]:
        chosen = min(waiting, key=lambda r: r["reset_minutes"])
        return {
            "action": "defer",
            "resource": chosen["id"],
            "cash": 0.0,
            "checks": checks,
            "reason": (
                f"free quota exhausted for {chosen['id']}; deferring {chosen['reset_minutes']} min "
                f"(within {request['deadline_minutes']} min deadline) and rechecking at wake-up"
            ),
            "wake_in_minutes": chosen["reset_minutes"],
        }

    # 3. Use cheapest available paid route within authorised budget
    paid = [r for r in eligible if r["available"] and r["cash"] <= request["budget"]]
    if paid:
        chosen = min(paid, key=lambda r: (r["cash"], r["allocation"], r["id"]))
        return {
            "action": "run",
            "resource": chosen["id"],
            "cash": chosen["cash"],
            "checks": checks,
            "reason": (
                f"free quotas unavailable or urgent; routed to paid {chosen['id']} "
                f"(${chosen['cash']:.6f} <= budget ${request['budget']})"
            ),
        }

    # 4. Abstain rather than routing to an unreliable model (Cohere/Dots/Qwen fail on age/combinations)
    return {
        "action": "abstain",
        "resource": None,
        "cash": 0.0,
        "checks": checks,
        "reason": (
            f"no reliable resource available for difficulty {difficulty} within "
            f"deadline ({request['deadline_minutes']} min) and budget (${request['budget']}); "
            "refusing fallback to low-accuracy TD 1 models"
        ),
    }


def scenarios():
    base = {
        "difficulty": 1,
        "high_impact": False,
        "can_wait": True,
        "deadline_minutes": 120,
        "budget": 0.30,
    }
    exhausted = [
        dict(r, available=False, reset_minutes=60) if r["access"] == "subscription" else dict(r)
        for r in RESOURCES
    ]
    return [
        ("simple", base, RESOURCES),
        ("complex", {**base, "difficulty": 3}, RESOURCES),
        ("deferrable", {**base, "difficulty": 3}, exhausted),
        ("urgent", {**base, "difficulty": 3, "can_wait": False, "deadline_minutes": 5}, exhausted),
        ("budget exhausted", {**base, "difficulty": 3, "can_wait": False, "budget": 0}, exhausted),
        ("high impact", {**base, "difficulty": 3, "high_impact": True}, RESOURCES),
        ("unknown capability", {**base, "difficulty": 4}, RESOURCES),
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", help="show only the named scenario")
    args = parser.parse_args()
    found = False
    for name, request, resources in scenarios():
        if args.scenario and name != args.scenario:
            continue
        found = True
        print(json.dumps({
            "scenario": name,
            "nature": "simulation",
            "request": request,
            "result": choose(request, resources),
        }))
    if not found:
        parser.error("unknown scenario")


if __name__ == "__main__":
    main()