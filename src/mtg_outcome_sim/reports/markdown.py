from pathlib import Path
from datetime import datetime, timezone


def generate_markdown_report(
    deck_name: str,
    deck_format: str,
    commander: str,
    card_count: int,
    tag_counts: dict[str, int],
    results: list[dict],
    output_path: Path | str,
) -> Path:
    """Generate a Markdown report file.

    Args:
        deck_name: Name of the deck (filename or custom).
        deck_format: Format string (e.g. 'commander', 'standard').
        commander: Commander name (empty string if not Commander).
        card_count: Total number of cards in the deck.
        tag_counts: Mapping of tag name -> count in deck.
        results: List of result dicts, each with keys:
            name, type, probability, method, and optionally
            iterations, by_turn.
        output_path: Where to write the Markdown report.

    Returns:
        Path to the generated report file.
    """
    lines = [
        "# MTG Outcome Simulation Report",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Deck",
        "",
        f"- **Name:** {deck_name}",
        f"- **Format:** {deck_format}",
        f"- **Commander:** {commander}",
        f"- **Total Cards:** {card_count}",
        "",
        "### Tag Distribution",
        "",
        "| Tag | Count |",
        "|-----|-------|",
    ]
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        lines.append(f"| {tag} | {count} |")

    lines.extend([
        "",
        "## Outcomes",
        "",
    ])

    for r in results:
        pct = f"{r['probability']:.2%}"
        lines.extend([
            f"### {r['name']}",
            "",
            f"- **Probability:** {pct}",
            f"- **Method:** {r['method']}",
        ])
        if "by_turn" in r:
            lines.append(f"- **By Turn:** {r['by_turn']}")
        if "iterations" in r and r["method"] == "Monte Carlo":
            lines.append(f"- **Iterations:** {r['iterations']:,}")
        lines.append("")

    path = Path(output_path)
    path.write_text("\n".join(lines))
    return path
