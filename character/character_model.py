import json
import os

class CharacterModel:
    """Model for managing character data within a specific campaign."""
    def __init__(self, campaign_path, name, rule_set_name):
        self.campaign_path = campaign_path
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        self.data_dir = os.path.join(self.campaign_path, 'characters')
        # This check is good practice, though the campaign model creates it.
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def set_attribute(self, attribute, value): self.attributes[attribute] = value
    def set_skill(self, skill, value): self.skills[skill] = value

    def to_dict(self):
        return {
            'name': self.name, 'rule_set': self.rule_set_name, 
            'attributes': self.attributes, 'skills': self.skills, 'inventory': self.inventory
        }

    @classmethod
    def from_dict(cls, campaign_path, data):
        """Creates a CharacterModel instance from a dictionary."""
        char = cls(campaign_path, data['name'], data['rule_set'])
        char.attributes = data.get('attributes', {})
        char.skills = data.get('skills', {})
        char.inventory = data.get('inventory', [])
        return char

    def save(self):
        """Saves the character data to a JSON file in the campaign's character folder."""
        filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(campaign_path, character_name):
        """Loads a character's data from a specific campaign."""
        data_dir = os.path.join(campaign_path, 'characters')
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath): return None
        with open(filepath, 'r') as f:
            data = json.load(f)
            return CharacterModel.from_dict(campaign_path, data)

    @staticmethod
    def get_for_ruleset(campaign_path, rule_set_name):
        """Gets characters for a ruleset from within a specific campaign."""
        data_dir = os.path.join(campaign_path, 'characters')
        if not os.path.exists(data_dir): return []
        
        valid_characters = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data.get('rule_set') == rule_set_name:
                            valid_characters.append(data.get('name'))
                except (json.JSONDecodeError, KeyError): continue
        return sorted(valid_characters)

    @staticmethod
    def delete(campaign_path, character_name):
        """Deletes a character's file from a specific campaign."""
        data_dir = os.path.join(campaign_path, 'characters')
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False