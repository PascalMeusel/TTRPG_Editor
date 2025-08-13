import json
import os

class RulesModel:
    """Model for managing TTRPG rule sets (loading, saving, listing)."""
    def __init__(self, rules_dir='data/rule_sets'):
        self.rules_dir = rules_dir
        if not os.path.exists(self.rules_dir):
            os.makedirs(self.rules_dir)

    def save_rule_set(self, name, attributes, skills, formulas):
        rule_set = { 'name': name, 'attributes': attributes, 'skills': skills, 'formulas': formulas }
        filepath = os.path.join(self.rules_dir, f"{name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(rule_set, f, indent=4)

    def load_rule_set(self, name):
        filepath = os.path.join(self.rules_dir, f"{name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            return json.load(f)

    def get_all_rule_sets(self):
        if not os.path.exists(self.rules_dir):
            return []
        return sorted([f.replace('.json', '').replace('_', ' ').title() for f in os.listdir(self.rules_dir) if f.endswith('.json')])