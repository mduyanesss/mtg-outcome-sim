import json
from pathlib import Path
from datetime import datetime, timezone


def generate_json_report(
    deck_name: str,
    deck_format: str,
    commander: str,
    card_count: int,
    tag_counts: dict[str, int],
    results: list[dict],
    output_path: Path | str,
    mana_curve_data: list[dict] | None = None,
) -> Path:
    """Generate a JSON report file.

    Args:
        deck_name: Name of the deck (filename or custom).
        deck_format: Format string (e.g. 'commander', 'standard').
        commander: Commander name (empty string if not Commander).
        card_count: Total number of cards in the deck.
        tag_counts: Mapping of tag name -> count in deck.
        results: List of result dicts, each with keys:
            name, type, probability, method, and optionally
            iterations, by_turn.
        output_path: Where to write the JSON report.
        mana_curve_data: Optional mana curve data from simulate_mana_curve_mc.

    Returns:
        Path to the generated report file.
    """
    report: dict = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "deck": {
            "name": deck_name,
            "format": deck_format,
            "commander": commander,
            "total_cards": card_count,
            "tag_distribution": tag_counts,
        },
        "outcomes": [],
    }
    for r in results:
        outcome_entry = {
            "name": r["name"],
            "type": r["type"],
            "probability": round(r["probability"], 4),
            "method": r["method"],
        }
        if "iterations" in r:
            outcome_entry["iterations"] = r["iterations"]
        if "by_turn" in r:
            outcome_entry["by_turn"] = r["by_turn"]
        report["outcomes"].append(outcome_entry)

    if mana_curve_data:
        report["mana_curve"] = []
        for row in mana_curve_data:
            report["mana_curve"].append(
                {
                    "turn": row["turn"],
                    "mean_mana": round(row["mean_mana"], 2),
                    "median_mana": row["median_mana"],
                    "p10_mana": row["p10_mana"],
                    "p90_mana": row["p90_mana"],
                }
            )

    path = Path(output_path)
    path.write_text(json.dumps(report, indent=2))
    return path
