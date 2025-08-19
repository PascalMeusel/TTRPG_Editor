import json
import os

class NpcModel:
    """Model for managing NPC data within a specific campaign."""
    def __init__(self, campaign_path, name, rule_set_name):
        self.campaign_path = campaign_path
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        self.gm_notes = ""
        # NEW: Explicitly track current HP
        self.current_hp = None
        self.data_dir = os.path.join(self.campaign_path, 'npcs')
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def to_dict(self):
        """Converts the NPC object to a dictionary for saving."""
        # Ensure current_hp is set before saving
        if self.current_hp is None:
            self.current_hp = self.attributes.get("Hit Points", "10")
        return {
            'name': self.name, 'rule_set': self.rule_set_name, 'attributes': self.attributes,
            'skills': self.skills, 'inventory': self.inventory, 'gm_notes': self.gm_notes,
            'current_hp': self.current_hp
        }

    @classmethod
    def from_dict(cls, campaign_path, data):
        """Creates an NpcModel instance from a dictionary."""
        npc = cls(campaign_path, data['name'], data['rule_set'])
        npc.attributes = data.get('attributes', {})
        npc.skills = data.get('skills', {})
        npc.gm_notes = data.get('gm_notes', "")
        
        inventory_data = data.get('inventory', [])
        for item_entry in inventory_data:
            if 'equipped' not in item_entry:
                item_entry['equipped'] = False
        npc.inventory = inventory_data
        
        # Load current_hp, defaulting to Max HP if not found (for backward compatibility)
        max_hp = npc.attributes.get("Hit Points", "10")
        npc.current_hp = data.get('current_hp', max_hp)

        return npc

    def save(self):
        """Saves the NPC data to a JSON file in the campaign's NPC folder."""
        filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}.json")
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @staticmethod
    def load(campaign_path, npc_name):
        """Loads an NPC's data from a specific campaign."""
        data_dir = os.path.join(campaign_path, 'npcs')
        filepath = os.path.join(data_dir, f"{npc_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(filepath): return None
        with open(filepath, 'r') as f:
            data = json.load(f)
            return NpcModel.from_dict(campaign_path, data)

    @staticmethod
    def get_for_ruleset(campaign_path, rule_set_name):
        """Gets NPCs for a ruleset from within a specific campaign."""
        data_dir = os.path.join(campaign_path, 'npcs')
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
    def delete(campaign_path, npc_name):
        """Deletes an NPC's file from a specific campaign."""
        data_dir = os.path.join(campaign_path, 'npcs')
        filepath = os.path.join(data_dir, f"{npc_name.lower().replace(' ', '_')}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False