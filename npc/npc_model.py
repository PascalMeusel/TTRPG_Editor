import json
from database import Database

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
        """Saves the NPC data to the database."""
        db = Database(self.campaign_path)
        db.connect()
        npc_id = self.name.lower().replace(' ', '_')
        data_json = json.dumps(self.to_dict())
        db.execute(
            "INSERT OR REPLACE INTO npcs (id, name, rule_set, data) VALUES (?, ?, ?, ?)",
            (npc_id, self.name, self.rule_set_name, data_json)
        )
        db.close()

    @staticmethod
    def load(campaign_path, npc_name):
        """Loads a single NPC from the database by name."""
        db = Database(campaign_path)
        db.connect()
        npc_id = npc_name.lower().replace(' ', '_')
        row = db.fetchone("SELECT data FROM npcs WHERE id = ?", (npc_id,))
        db.close()
        if row:
            data = json.loads(row['data'])
            return NpcModel.from_dict(campaign_path, data)
        return None

    @staticmethod
    def get_all_for_ruleset(campaign_path, rule_set_name):
        """--- OPTIMIZED: Loads all NPCs for a ruleset in a single query. ---"""
        db = Database(campaign_path)
        db.connect()
        rows = db.fetchall("SELECT data FROM npcs WHERE rule_set = ?", (rule_set_name,))
        db.close()
        return [NpcModel.from_dict(campaign_path, json.loads(row['data'])) for row in rows]

    @staticmethod
    def delete(campaign_path, npc_name):
        """Deletes an NPC from the database."""
        db = Database(campaign_path)
        db.connect()
        npc_id = npc_name.lower().replace(' ', '_')
        db.execute("DELETE FROM npcs WHERE id = ?", (npc_id,))
        db.close()
        return True