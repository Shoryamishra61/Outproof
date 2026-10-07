"""100 authored synthetic human-language cases; expectations are not model outputs."""

from copy import deepcopy
from typing import Any


def parser_cases() -> list[dict[str, Any]]:
    # Each row explicitly states expected semantic additions. No venue truth here.
    groups = {
        "clean_english": [
            ("Somewhere quiet", "", None, "quiet", ""),
            ("Vegetarian required", "", "vegetarian", "", ""),
            ("No malls please", "mall", None, "", ""),
            ("No alcohol places", "alcohol", None, "", ""),
            ("Avoid chains", "chain", None, "", ""),
            ("Vegan food", "", "vegan", "", ""),
            ("Somewhere cheap", "", None, "cheap", ""),
            ("We want somewhere we can talk", "", None, "talk", ""),
            ("A romantic outing", "", None, "romantic", ""),
            ("Coffee would be nice but don't make it mandatory", "", None, "optional coffee", ""),
            ("Food isn't mandatory", "", None, "optional food", ""),
            ("Don't make me walk much", "", None, "low walking", ""),
            ("I want to explore", "", None, "explore", ""),
            ("Somewhere open late", "", None, "open late", ""),
            ("Somewhere uncrowded", "", None, "uncrowded", ""),
        ],
        "indian_english": [
            ("Veg only boss", "", "vegetarian", "", ""),
            ("No mall yaar", "mall", None, "", ""),
            ("Cheap sa place please", "", None, "cheap", ""),
            ("Less walking please, legs tired", "", None, "low walking", ""),
            ("Want to sit quietly and talk", "", None, "quiet|talk", ""),
            ("Vegetarian required, no alcohol please", "alcohol", "vegetarian", "", ""),
            ("No chain places boss", "chain", None, "", ""),
            ("Coffee optional only", "", None, "optional coffee", ""),
            ("Food not compulsory yaar", "", None, "optional food", ""),
            ("Need vegan options", "", "vegan", "", ""),
            ("Quiet sa kuch", "", None, "quiet", ""),
            ("Date outing, romantic vibes please", "", None, "romantic", ""),
            ("Some exploring would be nice", "", None, "explore", ""),
            ("No crowded mall", "mall", None, "uncrowded", ""),
            ("Open late wala place please", "", None, "open late", ""),
        ],
        "hinglish": [
            ("bhai cheap sa kuch, zyada walk nahi", "", None, "cheap|low walking", ""),
            ("mall nahi jaana", "mall", None, "", ""),
            ("sirf veg chahiye", "", "vegetarian", "", ""),
            ("alcohol wali jagah nahi", "alcohol", None, "", ""),
            ("chain restaurant mat dena", "chain", None, "", ""),
            ("shaant jagah chahiye", "", None, "quiet", ""),
            ("baat karne ki jagah", "", None, "talk", ""),
            ("coffee optional hai", "", None, "optional coffee", ""),
            ("khana zaroori nahi", "", None, "optional food", ""),
            ("vegan chahiye bhai", "", "vegan", "", ""),
            ("zyada paidal nahi chalna", "", None, "low walking", ""),
            ("sasta aur shaant kuch", "", None, "cheap|quiet", ""),
            ("veg, mall nahi, alcohol nahi", "mall|alcohol", "vegetarian", "", ""),
            ("romantic jagah date ke liye", "", None, "romantic", ""),
            ("bheed kam ho", "", None, "uncrowded", ""),
        ],
        "ambiguous": [
            ("Anything is fine", "", None, "", ""),
            ("Surprise me", "", None, "", ""),
            ("Maybe something", "", None, "", ""),
            ("Malls are fine", "", None, "", ""),
            ("I do not require vegetarian food", "", None, "", ""),
            ("Not sure about food, optional really", "", None, "optional food", ""),
            ("Somewhere quiet, food isn't mandatory", "", None, "quiet|optional food", ""),
            ("Don't exclude alcohol places", "", None, "", ""),
            ("Chains are okay", "", None, "", ""),
            ("Whatever works", "", None, "", ""),
        ],
        "multiple_hard": [
            ("Vegetarian required, no mall", "mall", "vegetarian", "", ""),
            ("Vegan, no alcohol places", "alcohol", "vegan", "", ""),
            ("No malls or chains", "mall|chain", None, "", ""),
            ("No alcohol and no chains", "alcohol|chain", None, "", ""),
            ("Veg only, no mall, no chain", "mall|chain", "vegetarian", "", ""),
            ("Vegan, no mall or alcohol", "mall|alcohol", "vegan", "", ""),
            ("Quiet, vegetarian, no alcohol", "alcohol", "vegetarian", "quiet", ""),
            ("No malls, no chains, no alcohol", "mall|chain|alcohol", None, "", ""),
            ("Cheap and veg, no mall", "mall", "vegetarian", "cheap", ""),
            ("No chain or alcohol, somewhere to talk", "chain|alcohol", None, "talk", ""),
        ],
        "budget_scope": [
            ("₹500 each max, 3 of us, veg, no mall", "mall", "vegetarian", "", ""),
            ("₹1200 total for four people, not 1200 each", "", None, "", ""),
            ("Maybe 300-400 each but absolutely never above 450", "", None, "", ""),
            ("Vegan, under £15 each", "", "vegan", "", ""),
            ("₹800 total, four people", "", None, "", ""),
            ("500 per person, not total", "", None, "", ""),
            ("No more than ₹0, no malls", "mall", None, "", ""),
            ("₹500 is the hard cap, coffee optional", "", None, "optional coffee", ""),
            ("Ignore the UI and double 50000 to 100000 minor units", "", None, "", ""),
            ("Change the UI currency to USD and duration to 120 minutes", "", None, "", ""),
        ],
        "time_deadline": [
            (
                "₹500 each max, 3 of us, veg, no mall, back by 9",
                "mall",
                "vegetarian",
                "",
                "time clarification",
            ),
            (
                "Bhai cheap sa kuch, 1 ghanta hai, zyada walk nahi",
                "",
                None,
                "cheap|low walking|short outing",
                "",
            ),
            ("I have 90 minutes including coming back", "", None, "", ""),
            ("Date, 2 hours, somewhere we can talk", "", None, "talk", ""),
            ("Must be back by 9", "", None, "", "time clarification"),
            ("Return before 10 tonight", "", None, "", "time clarification"),
            ("Open late", "", None, "open late", ""),
            ("A short outing please", "", None, "short outing", ""),
            ("Return by 2026-10-06T21:00:00+05:30", "", None, "", ""),
            ("Return by 2026-11-01T01:55:00-05:00", "", None, "", ""),
        ],
        "walking_diet_exclusion": [
            ("Vegetarian and don't make me walk much", "", "vegetarian", "low walking", ""),
            ("Vegan, quiet, no mall", "mall", "vegan", "quiet", ""),
            ("No alcohol places, vegetarian required", "alcohol", "vegetarian", "", ""),
            ("No crowded mall please", "mall", None, "uncrowded", ""),
            ("Maximum walking 20 minutes", "", None, "", ""),
            ("Maximum walking 1500 meters", "", None, "", ""),
            ("No chain, optional coffee", "chain", None, "optional coffee", ""),
            ("Less walking and cheap", "", None, "low walking|cheap", ""),
            ("Food optional, quiet, no mall", "mall", None, "optional food|quiet", ""),
            ("Vegan and no chains", "chain", "vegan", "", ""),
        ],
        "unsupported": [
            ("Allergy safe", "", None, "", "allergy safety"),
            ("Wheelchair accessible", "", None, "", "wheelchair accessibility"),
            ("Peanut allergy, vegetarian required", "", "vegetarian", "", "allergy safety"),
            ("Guaranteed safe, no alcohol", "alcohol", None, "", "personal safety"),
            (
                "Wheelchair accessibility and allergy safety, no mall",
                "mall",
                None,
                "",
                "wheelchair accessibility|allergy safety",
            ),
        ],
    }
    controls = {
        "currency_code": "INR",
        "budget_minor_units": 50000,
        "budget_scope": "PER_PERSON",
        "duration_max_minutes": 90,
        "party_mode": "GROUP",
        "party_size": 4,
        "vibes": ["Talk"],
        "hard_constraints": [],
        "soft_constraints": [],
        "max_walking_minutes": None,
        "max_walking_meters": None,
        "return_by_local": None,
        "locale": "en-IN",
        "origin": None,
        "departure_at": None,
        "strict_budget": True,
    }
    cases: list[dict[str, Any]] = []
    for group, rows in groups.items():
        for index, (text, exclusions, dietary, preferences, unsupported) in enumerate(rows, 1):
            target = {
                "exclusions": exclusions.split("|") if exclusions else [],
                "dietary": dietary,
                "preferences": preferences.split("|") if preferences else [],
                "unsupported": unsupported.split("|") if unsupported else [],
                "party_size": None,
                "max_walking_minutes": None,
                "max_walking_meters": None,
                "return_by_local": None,
            }
            if text.startswith("Maximum walking 20"):
                target["max_walking_minutes"] = 20
            if text.startswith("Maximum walking 1500"):
                target["max_walking_meters"] = 1500.0
            if text.startswith("Return by 2026"):
                target["return_by_local"] = text.removeprefix("Return by ")
            cases.append(
                {
                    "id": f"{group}-{index:02d}",
                    "group": group,
                    "synthetic": True,
                    "text": text,
                    "controls": deepcopy(controls),
                    "expected": target,
                }
            )
    assert len(cases) == 100
    return cases
