import random

class NpcGeneratorModel:
    """
    A service model for generating random but plausible NPC data.
    This model has been significantly expanded to provide a vast degree of variety,
    addressing the request for a much larger pool of content. It procedurally combines
    names, traits, backstories, and items to create unique and memorable characters.
    """

    def __init__(self):
        # --- Expanded Archetypes ---
        # Defines core concepts, stat priorities, and thematic items.
        self.archetypes = {
            "Warrior": {
                "primary_stats": ["Strength", "Hit Points", "Athletics"],
                "occupations": ["Town Guard", "Mercenary", "Veteran Soldier", "Gladiator", "Bandit Chief"],
                "items": [
                    {"name": "Longsword", "type": "Weapon", "description": "A standard, reliable steel longsword.", "modifiers": []},
                    {"name": "Chainmail Armor", "type": "Armor", "description": "A suit of interlocking metal rings.", "modifiers": [{"stat": "Dodge Chance", "value": -2}]}
                ]
            },
            "Rogue": {
                "primary_stats": ["Dexterity", "Stealth", "Sleight of Hand"],
                "occupations": ["Thief", "Spy", "Assassin", "Smuggler", "Locksmith"],
                "items": [
                    {"name": "Shortsword", "type": "Weapon", "description": "A light, quick blade, perfect for close quarters.", "modifiers": []},
                    {"name": "Leather Armor", "type": "Armor", "description": "Armor made of hardened leather, quiet and flexible.", "modifiers": []},
                    {"name": "Thieves' Tools", "type": "Miscellaneous", "description": "A set of lockpicks and other useful tools.", "modifiers": [{"stat": "Sleight of Hand", "value": 2}]}
                ]
            },
            "Mage": {
                "primary_stats": ["Intelligence", "Magic", "Arcana"],
                "occupations": ["Court Wizard", "Hedge Mage", "Alchemist", "Enchanter", "Librarian"],
                "items": [
                    {"name": "Wizard Robes", "type": "Armor", "description": "Flowing robes, embroidered with minor protective runes.", "modifiers": []},
                    {"name": "Gnarled Staff", "type": "Weapon", "description": "A twisted oaken staff, cool to the touch.", "modifiers": [{"stat": "Magic", "value": 1}]}
                ]
            },
            "Cleric": {
                "primary_stats": ["Wisdom", "Faith", "Medicine"],
                "occupations": ["Temple Priest", "Traveling Healer", "Inquisitor", "Shrine Keeper"],
                "items": [
                    {"name": "Mace", "type": "Weapon", "description": "A blunt-force weapon favored by those who shun blades.", "modifiers": []},
                    {"name": "Holy Symbol", "type": "Miscellaneous", "description": "A silver amulet depicting a sacred deity.", "modifiers": [{"stat": "Faith", "value": 1}]},
                    {"name": "Healer's Kit", "type": "Consumable", "description": "A kit containing bandages, salves, and herbs.", "modifiers": []}
                ]
            },
            "Ranger": {
                "primary_stats": ["Dexterity", "Survival", "Perception"],
                "occupations": ["Hunter", "Scout", "Bounty Hunter", "Wilderness Guide"],
                "items": [
                    {"name": "Longbow", "type": "Weapon", "description": "A powerful bow made of yew.", "modifiers": []},
                    {"name": "Studded Leather", "type": "Armor", "description": "Leather armor reinforced with metal studs.", "modifiers": []}
                ]
            },
            "Noble": {
                "primary_stats": ["Charisma", "Persuasion", "Deception"],
                "occupations": ["Diplomat", "Scheming Courtier", "Disgraced Heir", "Ambitious Lord"],
                "items": [
                    {"name": "Fine Clothes", "type": "Armor", "description": "An immaculate outfit of silk and velvet.", "modifiers": []},
                    {"name": "Signet Ring", "type": "Miscellaneous", "description": "A ring bearing the crest of a noble family.", "modifiers": [{"stat": "Charisma", "value": 1}]}
                ]
            },
            "Artisan": {
                "primary_stats": ["Dexterity", "Crafting"],
                "occupations": ["Blacksmith", "Jeweler", "Carpenter", "Tailor", "Brewer"],
                "items": [
                    {"name": "Artisan's Tools", "type": "Miscellaneous", "description": "A set of high-quality tools for a specific craft.", "modifiers": [{"stat": "Crafting", "value": 2}]},
                    {"name": "Leather Apron", "type": "Armor", "description": "A heavy apron for protection while working.", "modifiers": []}
                ]
            },
            "Commoner": {
                "primary_stats": [],
                "occupations": ["Farmer", "Innkeeper", "Beggar", "Rat Catcher", "Dockworker"],
                "items": [
                    {"name": "Simple Clothes", "type": "Armor", "description": "A commoner's tunic and trousers.", "modifiers": []},
                    {"name": "Wood Axe", "type": "Weapon", "description": "A simple axe for chopping wood.", "modifiers": []}
                ]
            }
        }

        # --- Expanded Name Lists (by cultural theme) ---
        self.names = {
            "Human (Common)": ["Alden", "Bram", "Cole", "Darian", "Erik", "Finn", "Garret", "Hale", "Joric", "Kael", "Loric", "Merek", "Nico", "Orin", "Perrin", "Quinn", "Ronan", "Stellan", "Talon", "Vance", "Elara", "Faye", "Gwen", "Isolde", "Jessa", "Kiera", "Lyra", "Moira", "Nadia", "Oria", "Petra", "Rhea", "Seraphina", "Tessa", "Vera"],
            "Elven": ["Aelar", "Birel", "Caelen", "Dior", "Elros", "Faelar", "Galin", "Hador", "Ithron", "Laelon", "Mirek", "Nelor", "Orophin", "Paelias", "Raelon", "Soveliss", "Tassarion", "Valen", "Amriel", "Celebrian", "Doriella", "Elara", "Finduilas", "Galadriel", "Idril", "Luthien", "Mireth", "Nariel", "Oriana", "Rina", "Sariel", "Tinuvel", "Yavanna"],
            "Dwarven": ["Balin", "Borin", "Dain", "Durin", "Fili", "Gloin", "Hargin", "Ivor", "Kili", "Morin", "Norin", "Oin", "Rorin", "Thorin", "Urgon", "Amber", "Bera", "Dagna", "Elga", "Freyda", "Gisli", "Helga", "Ingra", "Lifsa", "Modi", "Olga", "Ragna", "Sigga", "Thora", "Urda"],
            "Orcish": ["Grom", "Thrag", "Azog", "Bolg", "Ugluk", "Grishnakh", "Shagrat", "Gorbag", "Muzgash", "Othrod", "Agron", "Borgakh", "Ghorza", "Lash", "Urzoga", "Shel", "Batul", "Snaga"]
        }
        self.surnames = ["Blackwood", "Stonehand", "Swiftwater", "Ironhide", "Moonwhisper", "Goldhand", "Ashworth", "Greycastle", "Redstream", "Deepdelver", "Oakenshield", "Bronzebeard", "Thunderforge", "Shatterstone", "Skullcrusher", "Bloodfist", "Ironjaw"]

        # --- Expanded Backstory Components ---
        self.origins = ["Born in the squalor of a city slum,", "Raised in a quiet, secluded village,", "A product of a minor but proud noble house,", "Trained from a young age in a monastic order,", "The sole survivor of a raided caravan,", "An outcast from their tribe for a forgotten taboo,", "A former soldier, weary of war,", "An apprentice who left their master under mysterious circumstances,", "A refugee from a land ravaged by blight,"]
        self.defining_events = ["they witnessed a terrible injustice that they were powerless to stop.", "they discovered a natural talent that set them apart from their peers.", "a close family member was lost to a plague.", "they were betrayed by a trusted friend, costing them everything.", "they stumbled upon an ancient ruin containing a dangerous secret.", "a prophecy foretold they would play a key role in a coming conflict.", "they were forced to make a terrible choice to survive.", "they inherited an artifact of unexpected power and importance."]
        self.goals = ["avenge their family's honor.", "find a cure for a lingering illness.", "start a new life, free from their past.", "achieve mastery in their chosen craft.", "pay off a crippling debt to a criminal organization.", "find a lost city rumored to hold great knowledge.", "earn enough money to buy back their ancestral home.", "expose a corrupt official who rules their homeland with an iron fist.", "understand the source of their own strange powers."]
        self.secrets = ["they are secretly an informant for the city guard.", "they are on the run, having faked their own death.", "they are the illegitimate child of a powerful noble.", "they are deeply in debt to a shadowy figure.", "the 'heirloom' they carry is actually a stolen artifact.", "they are terrified of something mundane, like birds or heights.", "they didn't actually earn their famous reputation; it was a lie that spiraled out of control."]
        
        # --- Expanded Personality & Voice Components ---
        self.positive_traits = ["Honorable", "Compassionate", "Brave", "Witty", "Patient", "Generous", "Optimistic", "Loyal", "Resourceful", "Curious", "Disciplined"]
        self.negative_traits = ["Arrogant", "Greedy", "Cowardly", "Cynical", "Impulsive", "Vengeful", "Paranoid", "Lazy", "Stubborn", "Deceitful", "Short-tempered"]
        self.voices = ["deep and gravelly", "high and melodic", "fast and clipped", "slow and deliberate", "hoarse and quiet", "booming and confident", "soft and breathy", "nasal and whiny", "smooth and charming"]
        self.mannerisms = ["constantly fidgets with a coin", "avoids direct eye contact", "has a noticeable limp", "often quotes obscure texts", "tends to stare off into the distance", "taps their fingers when impatient", "cracks their knuckles before a difficult task", "speaks with overly formal language", "has a habit of humming quietly"]
        self.appearances = ["a jagged scar across their left eye.", "impeccably clean and well-dressed.", "covered in a light layer of dirt and grime.", "several homemade tattoos on their arms.", "an air of weary sadness about them.", "a bright, infectious smile.", "eyes that seem to notice everything.", "a look of constant suspicion."]
        
    def generate(self, rule_set):
        """Generates a complete NPC data dictionary based on the ruleset."""
        archetype_name = random.choice(list(self.archetypes.keys()))
        archetype_data = self.archetypes[archetype_name]

        # 1. Generate Name based on a random culture
        culture = random.choice(list(self.names.keys()))
        name = f"{random.choice(self.names[culture])} {random.choice(self.surnames)}"

        # 2. Generate Stats
        stats = {}
        all_stats = rule_set.get('attributes', []) + list(rule_set.get('skills', {}).keys())
        for stat in all_stats:
            # Check if stat is in any part of the primary stats list (e.g., "Hit Points" in "primary_stats")
            if any(ps.lower() in stat.lower() for ps in archetype_data["primary_stats"]):
                 stats[stat] = str(random.randint(13, 17)) # High values
            else:
                 stats[stat] = str(random.randint(8, 12)) # Average values
        
        # 3. Generate Multi-Part Backstory
        backstory = (
            f"{random.choice(self.origins)} {name.split()[0]} {random.choice(self.defining_events)}\n\n"
            f"Now, they are driven to {random.choice(self.goals)} "
            f"All the while, they hide the fact that {random.choice(self.secrets)}"
        )

        # 4. Generate Detailed GM Notes
        gm_notes = (
            f"--- Backstory ---\n{backstory}\n\n"
            f"--- Appearance ---\nThey have {random.choice(self.appearances)}\n\n"
            f"--- Personality ---\n{random.choice(self.positive_traits)} but can be {random.choice(self.negative_traits).lower()}. "
            f"They are a {archetype_name} ({random.choice(archetype_data['occupations'])}) at heart.\n\n"
            f"--- Voice & Mannerisms ---\nVoice: {random.choice(self.voices)}. Mannerisms: {random.choice(self.mannerisms)}."
        )

        # 5. Get Suggested Items
        items_to_create = archetype_data["items"]

        return {
            "name": name,
            "stats": stats,
            "gm_notes": gm_notes,
            "items_to_create": items_to_create
        }