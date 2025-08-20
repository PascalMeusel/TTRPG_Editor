import random

class NpcGeneratorModel:
    """
    A service model for generating random but plausible NPC data, now with awareness
    of multiple TTRPG systems and genres.
    """

    def __init__(self):
        # The entire data structure is now organized by game system/genre.
        self.systems = {
            "D&D / Fantasy": {
                "keywords": ["Strength", "Dexterity", "Constitution", "Wisdom", "Charisma", "Intelligence"],
                "archetypes": {
                    "Fighter": {
                        "primary_stats": ["Strength", "Hit Points"], "occupations": ["Town Guard", "Mercenary", "Veteran", "Gladiator"],
                        "items": [{"name": "Longsword", "type": "Weapon", "description": "A standard steel longsword.", "modifiers": []}, {"name": "Chainmail Armor", "type": "Armor", "description": "A suit of interlocking metal rings.", "modifiers": [{"stat": "Dodge Chance", "value": -2}]}]
                    },
                    "Rogue": {
                        "primary_stats": ["Dexterity", "Stealth"], "occupations": ["Thief", "Spy", "Assassin", "Scout"],
                        "items": [{"name": "Dagger", "type": "Weapon", "description": "A small, easily concealed dagger.", "modifiers": []}, {"name": "Leather Armor", "type": "Armor", "description": "Armor made of hardened leather.", "modifiers": []}]
                    },
                    "Wizard": {
                        "primary_stats": ["Intelligence", "Arcana"], "occupations": ["Hedge Mage", "Court Wizard", "Scholar"],
                        "items": [{"name": "Wizard Robes", "type": "Armor", "description": "Flowing robes with arcane embroidery.", "modifiers": []}, {"name": "Quarterstaff", "type": "Weapon", "description": "A sturdy oaken staff.", "modifiers": [{"stat": "Magic", "value": 1}]}]
                    },
                    "Cleric": {
                        "primary_stats": ["Wisdom", "Medicine"], "occupations": ["Acolyte", "Traveling Healer", "Temple Priest"],
                        "items": [{"name": "Mace", "type": "Weapon", "description": "A blunt-force weapon favored by clerics.", "modifiers": []}, {"name": "Holy Symbol", "type": "Miscellaneous", "description": "A silver amulet of a deity.", "modifiers": [{"stat": "Wisdom", "value": 1}]}]
                    },
                    "Barbarian": {
                        "primary_stats": ["Strength", "Constitution", "Intimidation"], "occupations": ["Tribal Outcast", "Raider", "Pit Fighter"],
                        "items": [{"name": "Greataxe", "type": "Weapon", "description": "A massive, intimidating axe.", "modifiers": []}, {"name": "Hide Armor", "type": "Armor", "description": "Armor made from the thick hides of beasts.", "modifiers": []}]
                    },
                },
                "names": ["Alden", "Bram", "Faye", "Gwen", "Ronan", "Seraphina", "Kael", "Moira"],
                "surnames": ["Blackwood", "Stonehand", "Swiftwater", "Greycastle", "Oakenshield"],
                "origins": ["Raised in a quiet farming village,", "Trained from a young age in a remote monastery,", "The sole survivor of a goblin raid on their caravan,"],
                "goals": ["avenge a fallen mentor.", "find a lost family heirloom.", "reclaim their ancestral lands from orcs."],
                "secrets": ["is secretly a member of the thieves' guild.", "possesses a cursed magic item they cannot get rid of.", "is the illegitimate heir to a minor noble house."],
            },
            "Cyberpunk": {
                "keywords": ["Reflexes", "Tech", "Cool", "Body", "Empathy"],
                "archetypes": {
                    "Solo": {
                        "primary_stats": ["Reflexes", "Body", "Handguns", "Rifles"], "occupations": ["Corporate Enforcer", "Mercenary", "Cyberpsycho Hunter"],
                        "items": [{"name": "Heavy Pistol", "type": "Weapon", "description": "A reliable, high-caliber sidearm.", "modifiers": []}, {"name": "Armored Vest", "type": "Armor", "description": "Standard-issue kevlar body armor.", "modifiers": []}]
                    },
                    "Netrunner": {
                        "primary_stats": ["Intelligence", "Hacking", "Electronics"], "occupations": ["Data Thief", "System Saboteur", "Cyber-Detective"],
                        "items": [{"name": "Cyberdeck", "type": "Miscellaneous", "description": "A high-end deck for navigating the Net.", "modifiers": [{"stat": "Hacking", "value": 2}]}, {"name": "Light Pistol", "type": "Weapon", "description": "A small pistol for self-defense.", "modifiers": []}]
                    },
                    "Techie": {
                        "primary_stats": ["Tech", "Engineering", "Crafting"], "occupations": ["Ripperdoc", "Mechanic", "Weaponsmith"],
                        "items": [{"name": "Tech Toolkit", "type": "Miscellaneous", "description": "A full set of advanced cybernetic and electronic tools.", "modifiers": [{"stat": "Tech", "value": 2}]}, {"name": "Heavy Wrench", "type": "Weapon", "description": "It's for repairs, mostly.", "modifiers": []}]
                    },
                    "Fixer": {
                        "primary_stats": ["Cool", "Persuasion", "Streetwise"], "occupations": ["Information Broker", "Smuggler", "Gang Leader"],
                        "items": [{"name": "Burner Phone", "type": "Miscellaneous", "description": "An untraceable, disposable comms device.", "modifiers": []}, {"name": "Holdout Pistol", "type": "Weapon", "description": "A tiny pistol that's easy to conceal.", "modifiers": []}]
                    },
                },
                "names": ["Jax", "Kira", "Nash", "Rogue", "Spike", "V", "Yori", "Zane"],
                "surnames": ["Jones", "Tanaka", "Kowalski", "Singh", "Volkov", "Nix"],
                "origins": ["Grew up on the mean streets of the Combat Zone,", "An ex-corporate wage-slave who got burned,", "A nomad who left the clan for a life in the city,"],
                "goals": ["get enough eddies for a top-tier cybernetic upgrade.", "erase their past identity from a corporate database.", "take down the gang that wronged them."],
                "secrets": ["is secretly a corporate informant.", "has a piece of pre-Collapse tech they don't understand.", "is slowly succumbing to cyberpsychosis."],
            },
            "Call of Cthulhu / Horror": {
                "keywords": ["Power", "Education", "Sanity", "Luck"],
                "archetypes": {
                    "Investigator": {
                        "primary_stats": ["Investigation", "Library Use", "Spot Hidden"], "occupations": ["Private Detective", "Journalist", "Police Detective"],
                        "items": [{"name": ".38 Revolver", "type": "Weapon", "description": "A standard-issue six-shot revolver.", "modifiers": []}, {"name": "Trench Coat", "type": "Armor", "description": "A heavy coat, good for concealing things and staying anonymous.", "modifiers": []}]
                    },
                    "Professor": {
                        "primary_stats": ["Education", "Archaeology", "Occult"], "occupations": ["University Professor", "Museum Curator", "Antiquarian"],
                        "items": [{"name": "Ancient Tome", "type": "Miscellaneous", "description": "A leather-bound book filled with cryptic text.", "modifiers": [{"stat": "Sanity", "value": -5}]}, {"name": "Satchel", "type": "Miscellaneous", "description": "A leather bag for carrying books and artifacts.", "modifiers": []}]
                    },
                    "Dilettante": {
                        "primary_stats": ["Charisma", "Appraise", "Fine Art"], "occupations": ["Wealthy Heir", "Socialite", "Patron of the Arts"],
                        "items": [{"name": "Cane Sword", "type": "Weapon", "description": "An elegant walking cane with a concealed blade.", "modifiers": []}, {"name": "Expensive Suit", "type": "Armor", "description": "A perfectly tailored suit that opens doors in high society.", "modifiers": []}]
                    },
                },
                "names": ["Arthur", "Abigail", "Charles", "Eleanor", "Harvey", "Josephine", "Walter"],
                "surnames": ["Blackwood", "Armitage", "West", "Peaslee", "Derby", "Olmstead"],
                "origins": ["A respected academic at Miskatonic University,", "A hard-boiled detective haunted by a previous case,", "A wealthy socialite who dabbles in the occult for amusement,"],
                "goals": ["understand a recurring, horrifying nightmare.", "find out what happened to a missing colleague.", "debunk local superstitions, only to find they are real."],
                "secrets": ["found a strange artifact they can't get rid of.", "read a forbidden book that has started to warp their mind.", "is a member of a secret society that deals with the occult."],
            },
        }
        
        # Generic components, expanded for more variety
        self.adjectives = ["A weary", "A cheerful", "A suspicious", "A naive", "A grizzled", "An ambitious", "A cynical", "A paranoid", "A hopeful"]
        self.voices = ["deep and gravelly", "high and melodic", "fast and clipped", "slow and deliberate", "hoarse and quiet", "booming and confident", "soft and breathy", "nasal and whiny", "smooth and charming"]
        self.mannerisms = ["constantly fidgets with a coin", "avoids direct eye contact", "has a noticeable limp", "often quotes obscure texts", "tends to stare off into the distance", "taps their fingers when impatient", "cracks their knuckles", "speaks with overly formal language"]
        self.appearances = ["a jagged scar across their left eye.", "impeccably clean and well-dressed.", "covered in a light layer of grime.", "several strange tattoos on their arms.", "an air of weary sadness.", "a bright, infectious smile.", "eyes that seem to notice everything.", "a look of constant suspicion."]
    
    def _infer_system(self, rule_set):
        """Intelligently guesses the game system based on attribute names."""
        attributes = [attr.lower() for attr in rule_set.get('attributes', [])]
        for system_name, data in self.systems.items():
            matches = 0
            for keyword in data["keywords"]:
                if keyword.lower() in attributes:
                    matches += 1
            if matches >= 3: # A reasonable threshold for a match
                return system_name
        return "D&D / Fantasy" # Default if no match is found

    def generate(self, rule_set):
        """Generates a complete NPC data dictionary based on the inferred system."""
        system_name = self._infer_system(rule_set)
        system_data = self.systems[system_name]
        
        archetype_name = random.choice(list(system_data["archetypes"].keys()))
        archetype_data = system_data["archetypes"][archetype_name]

        name = f"{random.choice(system_data['names'])} {random.choice(system_data['surnames'])}"
        
        stats = {}
        all_stats = rule_set.get('attributes', []) + list(rule_set.get('skills', {}).keys())
        for stat in all_stats:
            if any(ps.lower() in stat.lower() for ps in archetype_data["primary_stats"]):
                stats[stat] = str(random.randint(13, 17))
            else:
                stats[stat] = str(random.randint(8, 12))
        
        backstory = (
            f"{random.choice(system_data['origins'])} {name.split()[0]} {random.choice(system_data['goals'])} "
            f"However, they harbor a secret: {name.split()[0]} {random.choice(system_data['secrets'])}"
        )
        
        gm_notes = (
            f"--- Backstory ---\n{backstory}\n\n"
            f"--- Appearance ---\nThey have {random.choice(self.appearances)}\n\n"
            f"--- Personality ---\n{random.choice(self.adjectives)} {random.choice(archetype_data['occupations']).lower()}.\n\n"
            f"--- Voice & Mannerisms ---\nVoice: {random.choice(self.voices)}. Mannerisms: {random.choice(self.mannerisms)}."
        )
        
        items_to_create = archetype_data["items"]

        return {
            "name": name,
            "stats": stats,
            "gm_notes": gm_notes,
            "items_to_create": items_to_create
        }