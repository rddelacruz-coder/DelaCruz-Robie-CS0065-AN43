"""Case-Based Reasoning demo for a Disaster Response Decision Support System.

Run: python TA3_CBR_Disaster_Response.py
The program saves retained cases to case_base.json beside this script.
"""

import json
from pathlib import Path

CASE_FILE = Path(__file__).with_name("case_base.json")

# Seed case base: prior disaster situations and their successful response plans.
INITIAL_CASES = [
    {
        "case_id": "D001",
        "hazard": "typhoon",
        "severity": 5,
        "people_affected": 1200,
        "resources": "adequate",
        "solution": "Open evacuation centers, deploy emergency teams, and distribute food, water, and medical supplies.",
    },
    {
        "case_id": "D002",
        "hazard": "flood",
        "severity": 4,
        "people_affected": 800,
        "resources": "limited",
        "solution": "Evacuate households in low-lying areas, prioritize older adults and children, and request boats and relief goods.",
    },
    {
        "case_id": "D003",
        "hazard": "earthquake",
        "severity": 5,
        "people_affected": 950,
        "resources": "moderate",
        "solution": "Set up safe assembly areas, assess damaged buildings, and coordinate search-and-rescue and medical teams.",
    },
    {
        "case_id": "D004",
        "hazard": "typhoon",
        "severity": 3,
        "people_affected": 350,
        "resources": "moderate",
        "solution": "Issue local warnings, prepare a nearby shelter, and pre-position basic food, water, and first-aid supplies.",
    },
    {
        "case_id": "D005",
        "hazard": "flood",
        "severity": 2,
        "people_affected": 120,
        "resources": "adequate",
        "solution": "Monitor water levels, clear drainage routes, and prepare transport for residents who may need evacuation.",
    },
]

# Weighted attributes sum to 1.00; population similarity is scaled to 1,500 people.
WEIGHTS = {"hazard": 0.35, "severity": 0.25, "people_affected": 0.25, "resources": 0.15}
RESOURCE_LEVEL = {"limited": 1, "moderate": 2, "adequate": 3}


def load_case_base():
    """Load retained experience, or start with the five sample cases."""
    if CASE_FILE.exists():
        try:
            with CASE_FILE.open("r", encoding="utf-8") as file:
                saved_cases = json.load(file)
            if isinstance(saved_cases, list) and saved_cases:
                return saved_cases
        except (OSError, json.JSONDecodeError):
            print("Saved case file could not be read; using the built-in cases.")
    return [case.copy() for case in INITIAL_CASES]


def save_case_base(cases):
    """Persist the case base as readable JSON for the next program run."""
    with CASE_FILE.open("w", encoding="utf-8") as file:
        json.dump(cases, file, indent=2, ensure_ascii=False)


def attribute_similarity(new_case, old_case):
    """Return a weighted similarity from 0.00 (different) to 1.00 (same)."""
    hazard_match = 1.0 if new_case["hazard"] == old_case["hazard"] else 0.0
    severity_match = 1 - abs(new_case["severity"] - old_case["severity"]) / 4
    population_match = max(
        0.0,
        1 - abs(new_case["people_affected"] - old_case["people_affected"]) / 1500,
    )
    resource_difference = abs(
        RESOURCE_LEVEL[new_case["resources"]] - RESOURCE_LEVEL[old_case["resources"]]
    )
    resource_match = 1 - resource_difference / 2

    return (
        WEIGHTS["hazard"] * hazard_match
        + WEIGHTS["severity"] * severity_match
        + WEIGHTS["people_affected"] * population_match
        + WEIGHTS["resources"] * resource_match
    )


def retrieve_cases(new_case, cases):
    """Rank past cases from most to least similar and return the ranking."""
    return sorted(
        ((attribute_similarity(new_case, case), case) for case in cases),
        key=lambda result: result[0],
        reverse=True,
    )


def adapt_solution(new_case, retrieved_case):
    """Reuse the retrieved plan, then adapt priorities to the new conditions."""
    actions = [retrieved_case["solution"]]

    if new_case["severity"] >= 4 and new_case["severity"] > retrieved_case["severity"]:
        actions.append("Escalate to the city or municipal emergency operations center and issue urgent public alerts.")
    elif new_case["severity"] <= 2:
        actions.append("Use a targeted response and continue monitoring before expanding the evacuation area.")

    if new_case["people_affected"] > retrieved_case["people_affected"]:
        actions.append("Increase shelter capacity, transport, and relief supplies to cover the larger population.")
    elif new_case["people_affected"] < retrieved_case["people_affected"]:
        actions.append("Scale the deployment to the smaller affected population while keeping reserve supplies ready.")

    if new_case["resources"] == "limited":
        actions.append("Prioritize people at greatest risk and request additional responders and supplies from nearby LGUs.")
    elif new_case["resources"] == "adequate" and retrieved_case["resources"] != "adequate":
        actions.append("Use available staff and supplies to open additional support points where needed.")

    return actions


def ask_choice(prompt, choices):
    """Prompt until the user enters one of the allowed choices."""
    choices_text = ", ".join(choices)
    while True:
        answer = input(f"{prompt} ({choices_text}): ").strip().lower()
        if answer in choices:
            return answer
        print(f"Please enter one of these values: {choices_text}.")


def ask_integer(prompt, minimum):
    """Prompt until a valid integer at or above the minimum is entered."""
    while True:
        try:
            value = int(input(prompt).strip())
            if value >= minimum:
                return value
        except ValueError:
            pass
        print(f"Enter a whole number of at least {minimum}.")


def main():
    cases = load_case_base()
    print("=" * 68)
    print("DISASTER RESPONSE CBR DECISION SUPPORT SYSTEM")
    print("=" * 68)
    print("Describe the new event. Similarity ranking uses the stored case attributes.\n")

    new_case = {
        "hazard": ask_choice("Hazard", ["typhoon", "flood", "earthquake"]),
        "severity": ask_integer("Severity (1 = low, 5 = critical): ", 1),
        "people_affected": ask_integer("Estimated people affected: ", 0),
        "resources": ask_choice("Available resources", ["limited", "moderate", "adequate"]),
    }
    if new_case["severity"] > 5:
        print("Severity is capped at 5 (critical).")
        new_case["severity"] = 5

    ranking = retrieve_cases(new_case, cases)
    best_score, best_case = ranking[0]
    adapted_actions = adapt_solution(new_case, best_case)

    print("\n--- New problem ---")
    print(
        f"{new_case['hazard'].title()} | severity {new_case['severity']}/5 | "
        f"{new_case['people_affected']:,} people affected | resources: {new_case['resources']}"
    )
    print("\n--- Similarity ranking ---")
    for score, case in ranking:
        print(f"{case['case_id']} ({case['hazard']}, severity {case['severity']}): {score:.3f}")
    print(f"\nRetrieved case: {best_case['case_id']} ({best_case['hazard']}) — similarity {best_score:.3f}")
    print("\n--- Adapted response plan ---")
    for number, action in enumerate(adapted_actions, start=1):
        print(f"{number}. {action}")

    retain = ask_choice("Retain this solved case for future use?", ["yes", "no"])
    if retain == "yes":
        new_id = f"D{len(cases) + 1:03d}"
        new_case["case_id"] = new_id
        new_case["solution"] = " ".join(adapted_actions)
        cases.append(new_case)
        save_case_base(cases)
        print(f"\nNew case saved as {new_id} in {CASE_FILE.name}.")
    else:
        print("\nCase was not retained.")

    print(f"\n--- Updated case base ({len(cases)} cases) ---")
    for case in cases:
        print(
            f"{case['case_id']}: {case['hazard']}, severity {case['severity']}, "
            f"{case['people_affected']:,} affected, resources {case['resources']}"
        )


if __name__ == "__main__":
    main()
