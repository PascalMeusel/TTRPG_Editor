import json
import os

class NpcModel:
    """Model for managing NPC data."""
    def __init__(self, name, rule_set_name):
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        self.gm_notes = ""
        self.loot = []
        self.data_dir = 'data/npcs'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def to_dict(self):
        return {
            'name': self.name, 'rule_set': self.rule_set_name, 'attributes': self.attributes,
            'skills': self.skills, 'inventory': self.inventory, 'gm_notes': self.gm_notes, 'loot': self.loot
        }

    @classmethod
    def from_dict(cls, data):
        npc = cls(data['name'], data['rule_set'])
        npc.attributes = data.get('attributes', {})
        npc.skills = data.get('skills', {})
        npc.inventory = data.get('inventory', [])
        npc.gm_notes = data.get('gm_notes', "")
        npc.loot = data.get('loot', [])
        return npc

    def save(self):
        filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(npc_name, data_dir='data/npcs'):
        filepath = os.path.join(data_dir, f"{npc_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath): return None
        with open(filepath, 'r') as f:
            return NpcModel.from_dict(json.load(f))

    @staticmethod
    def get_for_ruleset(rule_set_name, data_dir='data/npcs'):
        if not os.path.exists(data_dir): return []
        valid_npcs = []
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(data_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        if data.get('rule_set') == rule_set_name:
                            valid_npcs.append(data.get('name'))
                except (json.JSONDecodeError, KeyError): continue
        return sorted(valid_npcs)

    @staticmethod
    def delete(npc_name, data_dir='data/npcs'):
        filepath = os.path.join(data_dir, f"{npc_name.lower().replace(' ', '_')}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False