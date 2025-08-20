import random
import uuid

class CombatModel:
    """A stateful model for managing a single combat encounter."""
    def __init__(self):
        self.combatants = {}
        self.turn_order = []
        self.current_turn_index = -1
        self.is_active = False

    def add_combatant(self, base_model, is_pc):
        unique_id = str(uuid.uuid4())
        name = base_model.name
        if not is_pc:
            count = 1
            while any(c['name'] == name for c in self.combatants.values()):
                count += 1
                name = f"{base_model.name} {count}"
        try:
            dex_val = int(base_model.attributes.get("Dexterity", 10))
            max_hp_val = int(base_model.attributes.get("Hit Points", 10))
            current_hp_val = int(base_model.current_hp)
        except (ValueError, TypeError, AttributeError):
            dex_val, max_hp_val, current_hp_val = 10, 10, 10
        self.combatants[unique_id] = {
            "id": unique_id, "base_model": base_model, "name": name,
            "is_pc": is_pc, "initiative": 0, "dexterity": dex_val,
            "max_hp": max_hp_val, "current_hp": current_hp_val, "status": ""
        }
        return self.combatants[unique_id]

    def remove_combatant(self, combatant_id):
        if combatant_id in self.combatants:
            del self.combatants[combatant_id]

    def start_combat(self):
        if not self.combatants: return
        for combatant in self.combatants.values():
            dex_modifier = (combatant["dexterity"] - 10) // 2
            combatant["initiative"] = random.randint(1, 20) + dex_modifier
        self.turn_order = sorted(self.combatants.keys(), key=lambda cid: self.combatants[cid]["initiative"], reverse=True)
        self.is_active = True
        self.current_turn_index = 0

    def next_turn(self):
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
        self.is_active = False
        self.turn_order = []
        self.current_turn_index = -1
        self.combatants.clear()

    # --- NEW: Methods to manually adjust turn order ---
    def move_combatant_up(self, combatant_id):
        """Moves a combatant one position up in the turn order."""
        if combatant_id not in self.turn_order: return
        idx = self.turn_order.index(combatant_id)
        if idx > 0:
            self.turn_order[idx], self.turn_order[idx - 1] = self.turn_order[idx - 1], self.turn_order[idx]
            # If the moved combatant was the current one, update the index
            if self.current_turn_index == idx:
                self.current_turn_index -= 1
            elif self.current_turn_index == idx - 1:
                self.current_turn_index += 1

    def move_combatant_down(self, combatant_id):
        """Moves a combatant one position down in the turn order."""
        if combatant_id not in self.turn_order: return
        idx = self.turn_order.index(combatant_id)
        if idx < len(self.turn_order) - 1:
            self.turn_order[idx], self.turn_order[idx + 1] = self.turn_order[idx + 1], self.turn_order[idx]
            if self.current_turn_index == idx:
                self.current_turn_index += 1
            elif self.current_turn_index == idx + 1:
                self.current_turn_index -= 1