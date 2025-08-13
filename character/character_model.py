import json
import os

class CharacterModel:
    def __init__(self, name, rule_set_name):
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        self.data_dir = 'data/characters'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def set_attribute(self, attribute, value): self.attributes[attribute] = value
    def set_skill(self, skill, value): self.skills[skill] = value

    def to_dict(self):
        return { 'name': self.name, 'rule_set': self.rule_set_name, 'attributes': self.attributes, 'skills': self.skills, 'inventory': self.inventory }

    @classmethod
    def from_dict(cls, data):
        char = cls(data['name'], data['rule_set'])
        char.attributes = data.get('attributes', {})
        char.skills = data.get('skills', {})
        char.inventory = data.get('inventory', [])
        return char

    def save(self):
        filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(character_name, data_dir='data/characters'):
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath): return None
        with open(filepath, 'r') as f:
            data = json.load(f)
            return CharacterModel.from_dict(data)

    @staticmethod
    def get_for_ruleset(rule_set_name, data_dir='data/characters'):
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
    def delete(character_name, data_dir='data/characters'):
        filepath = os.path.join(data_dir, f"{character_name.lower().replace(' ', '_')}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False