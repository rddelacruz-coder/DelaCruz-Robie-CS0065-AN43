"""TA4: knowledge representation, RBR, and the complete CBR 4R cycle.

Run: python ta4_reasoning.py
Optional: --mode rbr|cbr, --facts examples/weather.json, --interactive,
          --revision "Updated solution", --save-cases retained_cases.json
Uses only the Python standard library (Python 3.10 or later).
"""

import argparse
from copy import deepcopy
import json
from pathlib import Path


# PART 1: six facts, organized into three explicit knowledge categories.
FACTS = {
    "temperature": 32, "humidity": 85, "is_raining": True,
    "wind_speed": 12, "is_daytime": True, "outdoor_activity": True,
}
CATEGORIES = {
    "temperature": ("temperature",),
    "weather": ("humidity", "is_raining", "wind_speed"),
    "activity_context": ("is_daytime", "outdoor_activity"),
}
# Numeric ranges normalize distance; units are Celsius, percent, and km/h.
RANGES = {"temperature": 50, "humidity": 100, "wind_speed": 100}
LIMITS = {"temperature": (-20, 50), "humidity": (0, 100),
          "wind_speed": (0, 200)}
CASE_BASE = [
    {"problem": {"temperature": 31, "humidity": 80,
                 "is_raining": True, "wind_speed": 10,
                 "is_daytime": True, "outdoor_activity": True},
     "solution": "Bring an umbrella, drink water, and move activity indoors."},
    {"problem": {"temperature": 27, "humidity": 55,
                 "is_raining": False, "wind_speed": 12,
                 "is_daytime": True, "outdoor_activity": True},
     "solution": "Proceed outdoors and carry drinking water."},
    {"problem": {"temperature": 20, "humidity": 70,
                 "is_raining": True, "wind_speed": 40,
                 "is_daytime": False, "outdoor_activity": False},
     "solution": "Stay indoors and secure loose outdoor items."},
]


def validate_facts(facts):
    """Reject incomplete facts, wrong types, and out-of-range numbers."""
    if not isinstance(facts, dict) or set(facts) != set(FACTS):
        raise ValueError("Facts must contain exactly the six sample keys.")
    for key, (low, high) in LIMITS.items():
        value = facts[key]
        if type(value) not in (int, float) or not low <= value <= high:
            raise ValueError(f"{key} must be a number from {low} to {high}.")
    for key in set(FACTS) - set(LIMITS):
        if type(facts[key]) is not bool:
            raise ValueError(f"{key} must be true or false.")


# PART 2: each function represents one explicit IF-THEN rule.
def rule_hot(facts):
    if facts["temperature"] > 30:
        return "Turn on a fan or air conditioner."


def rule_rain(facts):
    if facts["is_raining"]:
        return "Bring an umbrella."


def rule_humid_heat(facts):
    if facts["temperature"] > 30 and facts["humidity"] >= 80:
        return "Drink water and take breaks from the heat."


def rule_wind(facts):
    if facts["wind_speed"] >= 30:
        return "Secure loose outdoor items."


def rule_outdoor_rain(facts):
    if facts["outdoor_activity"] and facts["is_raining"]:
        return "Move the outdoor activity indoors."


RULES = (rule_hot, rule_rain, rule_humid_heat,
         rule_wind, rule_outdoor_rain)


def infer(facts):
    """Working memory is a copy; evaluate EVERY rule, collecting all actions."""
    validate_facts(facts)
    working_memory = deepcopy(facts)
    trace, actions = [], []
    for rule in RULES:
        action = rule(working_memory)
        trace.append((rule.__name__, bool(action)))
        if action:
            actions.append(action)
    return trace, actions


# PART 3: Retrieve -> Reuse -> Revise -> Retain.
def similarity(problem, past_problem):
    """Average six scores: normalized numeric closeness or Boolean equality."""
    validate_facts(problem)
    validate_facts(past_problem)
    total = 0.0
    for key in FACTS:
        if key in RANGES:
            distance = abs(problem[key] - past_problem[key])
            total += max(0.0, 1.0 - distance / RANGES[key])
        else:
            total += float(problem[key] == past_problem[key])
    return total / len(FACTS)


def retrieve(problem, case_base):
    """Score every case. The earlier case wins an exact similarity tie."""
    if not case_base:
        raise ValueError("Retrieval needs at least one past case.")
    scores = [similarity(problem, case["problem"]) for case in case_base]
    best = max(range(len(scores)), key=scores.__getitem__)
    return best, scores


def reuse(case):
    """Use the retrieved solution as the initial proposal."""
    return case["solution"]


def revise(solution, replacement=None):
    """A blank revision keeps the original; nonblank text replaces it."""
    return replacement.strip() if replacement and replacement.strip() else solution


def retain(problem, solution, case_base):
    """Store a separate copy so later edits cannot change past experience."""
    validate_facts(problem)
    if not isinstance(solution, str) or not solution.strip():
        raise ValueError("A retained solution must be nonblank text.")
    case_base.append({"problem": deepcopy(problem), "solution": solution.strip()})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("both", "rbr", "cbr"), default="both")
    parser.add_argument("--facts", type=Path, help="JSON with all six input facts")
    revision = parser.add_mutually_exclusive_group()
    revision.add_argument("--interactive", action="store_true")
    revision.add_argument("--revision", help="Manual replacement for the solution")
    parser.add_argument("--save-cases", type=Path, help="Save final case base as JSON")
    args = parser.parse_args(argv)
    if args.mode == "rbr" and (args.save_cases or args.interactive
                               or args.revision is not None):
        parser.error("Revision and case export require CBR mode.")
    facts = deepcopy(FACTS)
    try:
        if args.facts:
            facts = json.loads(args.facts.read_text(encoding="utf-8"))
        validate_facts(facts)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print("TA4 - KNOWLEDGE REPRESENTATION AND REASONING")
    print("Use case: planning activities in changing weather")
    print("\nINPUT - Knowledge Base (6 facts / 3 categories)")
    for category, keys in CATEGORIES.items():
        print(f"  {category}:")
        for key in keys:
            print(f"    {key}: {facts[key]}")

    if args.mode in ("both", "rbr"):
        trace, actions = infer(facts)
        print("\nPROCESS - Rule-Based Reasoning")
        for name, fired in trace:
            print(f"  {name}: {'FIRED' if fired else 'not fired'}")
        print("\nOUTPUT - Rule-Based Reasoning Actions:")
        for action in actions or ["No rule matched the current facts."]:
            print(f"- {action}")

    if args.mode in ("both", "cbr"):
        case_base = deepcopy(CASE_BASE)
        best, scores = retrieve(facts, case_base)
        print("\nPROCESS - Case-Based Reasoning (4R cycle)")
        print("1. RETRIEVE - Similarity of each past case:")
        for index, score in enumerate(scores, start=1):
            print(f"  Case {index}: {score:.2%}")
        print(f"  Selected: Case {best + 1}")
        proposal = reuse(case_base[best])
        print(f"2. REUSE - {proposal}")
        replacement = args.revision
        if args.interactive:
            try:
                replacement = input("Enter revision (Enter keeps solution): ")
            except EOFError:
                replacement = None
        final = revise(proposal, replacement)
        print(f"3. REVISE - {final}")
        print(f"  Solution {'unchanged' if final == proposal else 'manually revised'}.")
        before = len(case_base)
        retain(facts, final, case_base)
        print(f"4. RETAIN - Case base: {before} -> {len(case_base)} cases")
        print(f"\nOUTPUT - CBR Recommendation:\n{final}")
        if args.save_cases:
            try:
                args.save_cases.write_text(
                    json.dumps(case_base, indent=2) + "\n", encoding="utf-8")
            except OSError as error:
                parser.error(str(error))
            print(f"Saved final case base to: {args.save_cases}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
