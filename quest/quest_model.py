import json
import os
import uuid

class QuestModel:
    """Manages the quest database for a specific campaign."""
    def __init__(self, campaign_path):
        self.filepath = os.path.join(campaign_path, 'quests.json')

    def load_all_quests(self):
        """Loads the entire list of quests from quests.json."""
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_all_quests(self, quests_list):
        """Saves the entire list of quests to quests.json."""
        with open(self.filepath, 'w') as f:
            json.dump(quests_list, f, indent=4)

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