import json
import os
import uuid

class ItemModel:
    """Manages the item database for a specific campaign."""
    def __init__(self, campaign_path):
        self.campaign_path = campaign_path
        # Store campaign-specific data in the campaign folder itself
        self.filepath = os.path.join(self.campaign_path, 'items.json')

    def load_all_items(self):
        """Loads the entire list of items from items.json."""
        if not os.path.exists(self.filepath):
            return []
        with open(self.filepath, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    def save_all_items(self, items_list):
        """Saves the entire list of items to items.json."""
        with open(self.filepath, 'w') as f:
            json.dump(items_list, f, indent=4)

    def create_item(self, name, description, item_type, modifiers):
        """Creates a new item dictionary with a unique ID."""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "type": item_type,
            "modifiers": modifiers # e.g., [{"stat": "Strength", "value": 2}]
        }