# mtg-outcome-sim

Probabilistic Magic: The Gathering deck outcome simulator. Combines hypergeometric
distributions and Monte Carlo simulation to answer outcome questions about Commander
decks — not a rules engine.

## Installation

```bash
uv sync
```

## Usage

```bash
uv run mtg-outcome-sim import examples/decks/sample_commander.txt
```

## Status

MVP in development. CLI engine first, UX later.
