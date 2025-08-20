import json
import uuid
from database import Database

class ItemModel:
    """Manages the item database for a specific campaign."""
    def __init__(self, campaign_path):
        self.db = Database(campaign_path)

    def load_all_items(self):
        """Loads the entire list of items from the database."""
        self.db.connect()
        rows = self.db.fetchall("SELECT data FROM items")
        self.db.close()
        if not rows:
            return []
        return [json.loads(row['data']) for row in rows]

    def save_item(self, item_data):
        """Saves a single item to the database."""
        self.db.connect()
        self.db.execute(
            "INSERT OR REPLACE INTO items (id, data) VALUES (?, ?)",
            (item_data['id'], json.dumps(item_data))
        )
        self.db.close()

    def delete_item(self, item_id):
        """Deletes a single item from the database."""
        self.db.connect()
        self.db.execute("DELETE FROM items WHERE id = ?", (item_id,))
        self.db.close()

    def create_item(self, name, description, item_type, modifiers):
        """Creates a new item dictionary with a unique ID."""
        return {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "type": item_type,
            "modifiers": modifiers # e.g., [{"stat": "Strength", "value": 2}]
        }