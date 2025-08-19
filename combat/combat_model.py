import random
import uuid

class CombatModel:
    """A stateful model for managing a single combat encounter."""
    def __init__(self):
        self.combatants = {} # Dict of {unique_id: combatant_data}
        self.turn_order = [] # List of unique_ids, sorted by initiative
        self.current_turn_index = -1
        self.is_active = False

    def add_combatant(self, base_model, is_pc):
        """Adds a character or NPC to the combat roster."""
        unique_id = str(uuid.uuid4())
        
        name = base_model.name
        count = 1
        # Handle duplicate non-PC names
        if not is_pc:
            while any(c['name'] == name for c in self.combatants.values()):
                count += 1
                name = f"{base_model.name} {count}"
        
        try:
            dex_val = int(base_model.attributes.get("Dexterity", 10))
            hp_val = int(base_model.attributes.get("Hit Points", 10))
        except (ValueError, TypeError):
            dex_val, hp_val = 10, 10
            
        self.combatants[unique_id] = {
            "id": unique_id,
            "base_model": base_model,
            "name": name,
            "is_pc": is_pc,
            "initiative": 0,
            "dexterity": dex_val,
            "max_hp": hp_val,
            "current_hp": hp_val,
            "status": ""
        }
        return self.combatants[unique_id]

    def remove_combatant(self, combatant_id):
        """Removes a combatant from the roster."""
        if combatant_id in self.combatants:
            del self.combatants[combatant_id]

    def start_combat(self):
        """Rolls initiative, sorts the turn order, and starts the combat."""
        if not self.combatants:
            return
            
        for cid, combatant in self.combatants.items():
            dex_modifier = (combatant["dexterity"] - 10) // 2
            combatant["initiative"] = random.randint(1, 20) + dex_modifier
        
        self.turn_order = sorted(self.combatants.keys(), key=lambda cid: self.combatants[cid]["initiative"], reverse=True)
        self.is_active = True
        self.current_turn_index = 0

    def next_turn(self):
        """Advances to the next combatant in the turn order."""
        if not self.is_active or not self.turn_order: return
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)

    def get_current_combatant(self):
        if not self.is_active or not self.turn_order: return None
        combatant_id = self.turn_order[self.current_turn_index]
        return self.combatants.get(combatant_id)
        
    def apply_damage(self, combatant_id, amount):
        if combatant_id in self.combatants:
            self.combatants[combatant_id]["current_hp"] -= amount

    def apply_healing(self, combatant_id, amount):
        if combatant_id in self.combatants:
            combatant = self.combatants[combatant_id]
            combatant["current_hp"] = min(combatant["max_hp"], combatant["current_hp"] + amount)

    def set_status(self, combatant_id, status_text):
        if combatant_id in self.combatants:
            self.combatants[combatant_id]["status"] = status_text

    def reset_roster(self):
        """
        --- FIX: Fully resets the model for a new encounter. ---
        This is called by the controller after HP has been saved.
        """
        self.is_active = False
        self.turn_order = []
        self.current_turn_index = -1
        self.combatants.clear()