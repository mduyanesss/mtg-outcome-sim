import json
import tempfile
from pathlib import Path
from mtg_outcome_sim.reports.json_report import generate_json_report
from mtg_outcome_sim.reports.markdown import generate_markdown_report
from mtg_outcome_sim.reports.console import print_console_report


def test_json_report():
    results = [
        {
            "name": "Hit 3 lands by turn 3",
            "type": "minimum_cards_seen",
            "probability": 0.7363,
            "method": "Monte Carlo",
            "iterations": 100000,
            "by_turn": 3,
        },
        {
            "name": "Ramp by turn 2",
            "type": "has_tag",
            "probability": 0.5421,
            "method": "Hypergeometric",
            "by_turn": 2,
        },
    ]
    tag_counts = {"lands": 37, "ramp": 10, "draw": 8}
    with tempfile.TemporaryDirectory() as td:
        path = generate_json_report(
            "Test Deck",
            "commander",
            "Chatterfang",
            99,
            tag_counts,
            results,
            Path(td) / "report.json",
        )
        data = json.loads(path.read_text())
        assert data["deck"]["name"] == "Test Deck"
        assert data["deck"]["tag_distribution"]["lands"] == 37
        assert len(data["outcomes"]) == 2
        assert data["outcomes"][0]["probability"] == 0.7363
        assert "generated_at" in data


def test_markdown_report():
    results = [
        {
            "name": "Hit 3 lands by turn 3",
            "type": "minimum_cards_seen",
            "probability": 0.7363,
            "method": "Monte Carlo",
            "iterations": 100000,
            "by_turn": 3,
        },
    ]
    tag_counts = {"lands": 37, "ramp": 10}
    with tempfile.TemporaryDirectory() as td:
        path = generate_markdown_report(
            "Test Deck",
            "commander",
            "Chatterfang",
            99,
            tag_counts,
            results,
            Path(td) / "report.md",
        )
        content = path.read_text()
        assert "# MTG Outcome Simulation Report" in content
        assert "Test Deck" in content
        assert "37" in content
        assert "73.63%" in content


def test_json_report_rounds_probability():
    results = [
        {
            "name": "test",
            "type": "minimum_cards_seen",
            "probability": 0.123456,
            "method": "Monte Carlo",
            "iterations": 100000,
        },
    ]
    with tempfile.TemporaryDirectory() as td:
        path = generate_json_report(
            "d", "f", "c", 99, {}, results, Path(td) / "r.json"
        )
        data = json.loads(path.read_text())
        assert data["outcomes"][0]["probability"] == 0.1235  # rounded to 4 decimal places


def test_console_report_no_crash():
    """Console report should not raise exceptions."""
    results = [
        {
            "name": "Hit 3 lands",
            "type": "minimum_cards_seen",
            "probability": 0.73,
            "method": "Monte Carlo",
            "iterations": 100000,
            "by_turn": 3,
        },
    ]
    tag_counts = {"lands": 37}
    # Just verify it doesn't crash
    print_console_report("Test", tag_counts, results)
