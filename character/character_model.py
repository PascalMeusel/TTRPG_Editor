import json
import os

class CharacterModel:
    def __init__(self, campaign_path, name, rule_set_name):
        self.campaign_path = campaign_path
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        # --- NEW: Explicitly track current HP ---
        self.current_hp = None 
        self.data_dir = os.path.join(self.campaign_path, 'characters')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def set_attribute(self, attribute, value): self.attributes[attribute] = value
    def set_skill(self, skill, value): self.skills[skill] = value

    def to_dict(self):
        # Ensure current_hp is set before saving
        if self.current_hp is None:
            self.current_hp = self.attributes.get("Hit Points", "10")
        return {
            'name': self.name, 'rule_set': self.rule_set_name, 
            'attributes': self.attributes, 'skills': self.skills, 'inventory': self.inventory,
            'current_hp': self.current_hp
        }

    @classmethod
    def from_dict(cls, campaign_path, data):
        char = cls(campaign_path, data['name'], data['rule_set'])
        char.attributes = data.get('attributes', {})
        char.skills = data.get('skills', {})
        
        inventory_data = data.get('inventory', [])
        for item_entry in inventory_data:
            if 'equipped' not in item_entry: item_entry['equipped'] = False
        char.inventory = inventory_data

        # --- FIX: Load current_hp, defaulting to Max HP if not found ---
        max_hp = char.attributes.get("Hit Points", "10")
        char.current_hp = data.get('current_hp', max_hp)

        return char

    def save(self):
        """Saves the character data to a JSON file."""
        filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(campaign_path, character_name):
        data_dir = os.path.join(campaign_path, 'characters')
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath): return None
        with open(filepath, 'r') as f:
            data = json.load(f)
            return CharacterModel.from_dict(campaign_path, data)

    @staticmethod
    def get_for_ruleset(campaign_path, rule_set_name):
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
        data_dir = os.path.join(campaign_path, 'characters')
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False