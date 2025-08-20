import json
import uuid
from database import Database

class QuestModel:
    """Manages the quest database for a specific campaign."""
    def __init__(self, campaign_path):
        self.db = Database(campaign_path)

    def load_all_quests(self):
        """Loads the entire list of quests from the database."""
        self.db.connect()
        rows = self.db.fetchall("SELECT data FROM quests")
        self.db.close()
        if not rows:
            return []
        try:
            return [json.loads(row['data']) for row in rows]
        except json.JSONDecodeError:
            return []

    def save_quest(self, quest_data):
        """Saves a single quest to the database."""
        self.db.connect()
        self.db.execute(
            "INSERT OR REPLACE INTO quests (id, data) VALUES (?, ?)",
            (quest_data['id'], json.dumps(quest_data))
        )
        self.db.close()

    def delete_quest(self, quest_id):
        """Deletes a single quest from the database."""
        self.db.connect()
        self.db.execute("DELETE FROM quests WHERE id = ?", (quest_id,))
        self.db.close()

    def create_quest(self, title):
        """Creates a new quest dictionary with default values."""
        return {
            "id": str(uuid.uuid4()),
            "title": title,
            # --- FIX: New quests are now "Inactive" by default ---
            "status": "Inactive",
            "description": "",
            "objectives": [],
            "linked_npcs": [],
            "linked_items": []
        }