"""Fetch Scryfall oracle_text and type_line for all cards in the sample deck
plus common Commander staples. Uses the Scryfall /cards/collection endpoint
for efficient batch lookups. Writes deck_data.json in the web/ directory."""

import json
import sys
import time
import httpx

# All unique card names from examples/decks/sample_commander.txt
SAMPLE_DECK_CARDS = [
    "Chatterfang, Squirrel General",
    "Llanowar Elves",
    "Elvish Mystic",
    "Fyndhorn Elves",
    "Birds of Paradise",
    "Deathrite Shaman",
    "Elves of Deep Shadow",
    "Avacyn's Pilgrim",
    "Beast Whisperer",
    "Guardian Project",
    "Skullclamp",
    "Vampiric Tutor",
    "Demonic Tutor",
    "Assassin's Trophy",
    "Beast Within",
    "Nature's Claim",
    "Abrupt Decay",
    "Putrefy",
    "Mortality Spear",
    "Blood Artist",
    "Zulaport Cutthroat",
    "Poison-Tip Archer",
    "Bastion of Remembrance",
    "Ashnod's Altar",
    "Phyrexian Altar",
    "Viscera Seer",
    "Carrion Feeder",
    "Pitiless Plunderer",
    "Avenger of Zendikar",
    "Deranged Hermit",
    "Deep Forest Hermit",
    "Scurry Oak",
    "Chatter of the Squirrel",
    "Acorn Harvest",
    "Squirrel Nest",
    "Parallel Lives",
    "Doubling Season",
    "Rampant Growth",
    "Three Visits",
    "Nature's Lore",
    "Farseek",
    "Cultivate",
    "Kodama's Reach",
    "Farhaven Elf",
    "Wood Elves",
    "Sakura-Tribe Elder",
    "Night's Whisper",
    "Sign in Blood",
    "Read the Bones",
    "Harmonize",
    "Shamanic Revelation",
    "Toski, Bearer of Secrets",
    "Moldervine Reclamation",
    "Dark Prophecy",
    "Sylvan Library",
    "Eternal Witness",
    "Reclamation Sage",
    "Haywire Mite",
    "Scavenging Ooze",
    "Yawgmoth, Thran Physician",
    "Dictate of Erebos",
    "Grave Pact",
    "Nurturing Peatland",
    "Undergrowth Stadium",
    "Llanowar Wastes",
    "Woodland Cemetery",
    "Gilt-Leaf Palace",
    "Twilight Mire",
    "Deathcap Glade",
    "Darkbore Pathway",
    "Necroblossom Snarl",
    "Command Tower",
    "Bojuka Bog",
    "Swarmyard",
    "Phyrexian Tower",
    "Gaea's Cradle",
    "Cabal Coffers",
    "Urborg, Tomb of Yawgmoth",
    "Reliquary Tower",
    "Cavern of Souls",
    "Unclaimed Territory",
    "Ancient Tomb",
    "Path of Ancestry",
    "Boseiju, Who Endures",
    "Takenuma, Abandoned Mire",
    "Forest",
    "Swamp",
]

# Common Commander staples to add
COMMANDER_STAPLES = [
    "Sol Ring",
    "Arcane Signet",
    "Mana Crypt",
    "Mox Diamond",
    "Chrome Mox",
    "Mana Vault",
    "Grim Monolith",
    "Mox Opal",
    "Jeweled Lotus",
    "Mox Amber",
    "Fellwar Stone",
    "Talisman of Dominance",
    "Golgari Signet",
    "Mind Stone",
    "Commander's Sphere",
    "Dark Ritual",
    "Culling the Weak",
    "Cabal Ritual",
    "Entomb",
    "Reanimate",
    "Animate Dead",
    "Necromancy",
    "Dance of the Dead",
    "Worldly Tutor",
    "Green Sun's Zenith",
    "Finale of Devastation",
    "Chord of Calling",
    "Natural Order",
    "Eldritch Evolution",
    "Birthing Pod",
    "Diabolic Intent",
    "Razaketh, the Foulblooded",
    "Survival of the Fittest",
    "Fauna Shaman",
    "Protean Hulk",
    "Craterhoof Behemoth",
    "Triumph of the Hordes",
    "Overwhelming Stampede",
    "Torment of Hailfire",
    "Exsanguinate",
    "Necropotence",
    "Ad Nauseam",
    "Bolas's Citadel",
    "Sensei's Divining Top",
    "Mystic Remora",
    "Rhystic Study",
    "Wasteland",
    "Strip Mine",
    "Maze of Ith",
    "Yavimaya, Cradle of Growth",
    "Overgrown Tomb",
    "Bayou",
    "Verdant Catacombs",
    "Marsh Flats",
    "Misty Rainforest",
    "Polluted Delta",
    "Windswept Heath",
    "Bloodstained Mire",
    "Damnation",
    "Toxic Deluge",
    "Cyclonic Rift",
    "Swords to Plowshares",
    "Path to Exile",
    "Force of Will",
    "Fierce Guardianship",
    "Deflecting Swat",
    "Deadly Rollick",
    "Mana Drain",
    "Dockside Extortionist",
    "Smothering Tithe",
    "Esper Sentinel",
    "Dauthi Voidwalker",
    "Opposition Agent",
    "Drannith Magistrate",
    "Grand Abolisher",
    "Seedborn Muse",
    "Consecrated Sphinx",
    "The Great Henge",
    "Heroic Intervention",
    "Veil of Summer",
    "Autumn's Veil",
    "Go for the Throat",
    "Infernal Grasp",
    "Feed the Swarm",
    "Return to Nature",
    "Krosan Grip",
    "Force of Vigor",
    "Culling Ritual",
    "Bane of Progress",
    "Vandalblast",
    "Faithless Looting",
    "Wheel of Fortune",
    "Windfall",
]

BASE = "https://api.scryfall.com"
BATCH_SIZE = 70  # Scryfall collection endpoint limit


def fetch_batch(client: httpx.Client, names: list[str]) -> dict[str, dict]:
    """Fetch a batch of cards using the collection endpoint (POST by name)."""
    payload = {"identifiers": [{"name": n} for n in names]}
    try:
        r = client.post(
            f"{BASE}/cards/collection",
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        results = {}
        for card in data.get("data", []):
            results[card["name"]] = {
                "name": card["name"],
                "oracle_text": card.get("oracle_text", ""),
                "type_line": card.get("type_line", ""),
            }
        return results
    except Exception as e:
        print(f"  Batch error: {e}", file=sys.stderr)
        return {}


def main():
    all_cards = SAMPLE_DECK_CARDS + COMMANDER_STAPLES
    # Deduplicate while preserving order
    seen = set()
    unique_cards = []
    for c in all_cards:
        if c.lower() not in seen:
            seen.add(c.lower())
            unique_cards.append(c)

    print(f"Fetching data for {len(unique_cards)} unique cards...", file=sys.stderr)

    # First batch of sample deck cards (higher priority)
    sample_names = [c for c in unique_cards if c in SAMPLE_DECK_CARDS]
    staple_names = [c for c in unique_cards if c not in SAMPLE_DECK_CARDS]

    # Process in batches
    all_results: dict[str, dict] = {}
    all_names = sample_names + staple_names

    with httpx.Client() as client:
        for i in range(0, len(all_names), BATCH_SIZE):
            batch = all_names[i : i + BATCH_SIZE]
            print(f"  Fetching batch {i // BATCH_SIZE + 1}: {len(batch)} cards...", file=sys.stderr)
            results = fetch_batch(client, batch)
            all_results.update(results)
            # Small delay between batches
            if i + BATCH_SIZE < len(all_names):
                time.sleep(0.5)

    # Assemble output in original order
    output = []
    found = set()
    for name in unique_cards:
        # Try exact match first
        if name in all_results:
            output.append(all_results[name])
            found.add(name)
        else:
            # Try case-insensitive match
            matched = None
            for k, v in all_results.items():
                if k.lower() == name.lower():
                    matched = v
                    break
            if matched:
                # Use Scryfall's official name but log it
                output.append(matched)
                found.add(name)
            else:
                output.append({
                    "name": name,
                    "oracle_text": "",
                    "type_line": "",
                })

    good = sum(1 for c in output if c["oracle_text"])
    bad = sum(1 for c in output if not c["oracle_text"])

    output_path = "deck_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(output)} cards to {output_path}", file=sys.stderr)
    print(f"  With oracle_text: {good}", file=sys.stderr)
    print(f"  Without oracle_text: {bad}", file=sys.stderr)
    if bad > 0:
        print("Missing:", file=sys.stderr)
        for c in output:
            if not c["oracle_text"]:
                print(f"  - {c['name']}", file=sys.stderr)


if __name__ == "__main__":
    main()
