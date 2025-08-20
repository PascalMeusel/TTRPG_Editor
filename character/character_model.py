import json
from database import Database

class CharacterModel:
    def __init__(self, campaign_path, name, rule_set_name):
        self.campaign_path = campaign_path
        self.name = name
        self.rule_set_name = rule_set_name
        self.attributes = {}
        self.skills = {}
        self.inventory = []
        self.current_hp = None

    def set_attribute(self, attribute, value): self.attributes[attribute] = value
    def set_skill(self, skill, value): self.skills[skill] = value

    def to_dict(self):
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
        char.inventory = data.get('inventory', [])
        max_hp = char.attributes.get("Hit Points", "10")
        char.current_hp = data.get('current_hp', max_hp)
        return char

    def save(self):
        """Saves the character data to the database."""
        db = Database(self.campaign_path)
        db.connect()
        char_id = self.name.lower().replace(' ', '_')
        data_json = json.dumps(self.to_dict())
        db.execute(
            "INSERT OR REPLACE INTO characters (id, name, rule_set, data) VALUES (?, ?, ?, ?)",
            (char_id, self.name, self.rule_set_name, data_json)
        )
        db.close()

    @staticmethod
    def load(campaign_path, character_name):
        """Loads a single character from the database by name."""
        db = Database(campaign_path)
        db.connect()
        char_id = character_name.lower().replace(' ', '_')
        row = db.fetchone("SELECT data FROM characters WHERE id = ?", (char_id,))
        db.close()
        if row:
            data = json.loads(row['data'])
            return CharacterModel.from_dict(campaign_path, data)
        return None

    @staticmethod
    def get_all_for_ruleset(campaign_path, rule_set_name):
        """Loads all characters for a ruleset in a single query."""
        db = Database(campaign_path)
        db.connect()
        rows = db.fetchall("SELECT data FROM characters WHERE rule_set = ?", (rule_set_name,))
        db.close()
        return [CharacterModel.from_dict(campaign_path, json.loads(row['data'])) for row in rows]

    @staticmethod
    def delete(campaign_path, character_name):
        """Deletes a character from the database."""
        db = Database(campaign_path)
        db.connect()
        char_id = character_name.lower().replace(' ', '_')
        db.execute("DELETE FROM characters WHERE id = ?", (char_id,))
        db.close()
        return True