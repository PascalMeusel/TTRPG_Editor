from .combat_model import CombatModel
from .combat_view import CombatView
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
from character.character_model import CharacterModel
from npc.npc_model import NpcModel
from custom_dialogs import MessageBox

class CombatController:
    """Controller for the new Combat Tracker feature."""
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.model = CombatModel()
        self.view = CombatView(parent_frame)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.available_combatants = []

    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.update_combatant_lists()

    def update_combatant_lists(self):
        if not self.current_rule_set: return
        self.available_combatants = []
        
        char_controller = self.app_controller.get_loaded_controller(CharacterController)
        if char_controller:
            self.available_combatants.extend(char_controller.get_character_list())

        npc_controller = self.app_controller.get_loaded_controller(NpcController)
        if npc_controller:
            self.available_combatants.extend(npc_controller.get_npc_list())

        self.view.update_available_list(self.available_combatants, self)

    def add_to_roster(self, base_model):
        is_pc = isinstance(base_model, CharacterModel)
        if is_pc:
            for combatant in self.model.combatants.values():
                if combatant['base_model'].name == base_model.name and combatant['is_pc']:
                    MessageBox.showwarning("Warning", f"Player Character '{base_model.name}' is already in the encounter.", self.view.frame)
                    return
        self.model.add_combatant(base_model, is_pc)
        self.view.update_roster_list(self.model.combatants, self)

    def remove_from_roster(self, combatant_id):
        self.model.remove_combatant(combatant_id)
        self.view.update_roster_list(self.model.combatants, self)

    def start_combat(self):
        if not self.model.combatants:
            MessageBox.showinfo("Info", "Add combatants to the roster before starting combat.", self.view.frame)
            return
        self.model.start_combat()
        
        # --- FIX: Call the one-time UI setup, then update the list ---
        self.view.display_tracker_ui(self)
        self._update_turn_order_view()

    def next_turn(self):
        self.model.next_turn()
        self._update_turn_order_view()

    def end_combat(self):
        for combatant_data in self.model.combatants.values():
            base_model = combatant_data['base_model']
            final_hp = combatant_data['current_hp']
            base_model.current_hp = str(final_hp)
            base_model.save()
        self.model.reset_roster()
        self.view.clear_view()
        self.view.update_roster_list(self.model.combatants, self)
        self.app_controller.refresh_char_npc_sheet_if_loaded()
        self.update_combatant_lists()
        MessageBox.showinfo("Combat Ended", "Combat has ended. Current Hit Points have been saved.", self.view.frame)

    def apply_damage(self):
        combatant = self.model.get_current_combatant()
        if not combatant: return
        try:
            amount = int(self.view.action_value_entry.get())
            self.model.apply_damage(combatant['id'], amount)
            self._update_turn_order_view()
        except (ValueError, TypeError): pass
        self.view.action_value_entry.delete(0, 'end')

    def apply_healing(self):
        combatant = self.model.get_current_combatant()
        if not combatant: return
        try:
            amount = int(self.view.action_value_entry.get())
            self.model.apply_healing(combatant['id'], amount)
            self._update_turn_order_view()
        except (ValueError, TypeError): pass
        self.view.action_value_entry.delete(0, 'end')

    def set_status(self, combatant_id, text):
        self.model.set_status(combatant_id, text)

    def move_combatant_up(self, combatant_id):
        self.model.move_combatant_up(combatant_id)
        self._update_turn_order_view()

    def move_combatant_down(self, combatant_id):
        self.model.move_combatant_down(combatant_id)
        self._update_turn_order_view()

    def _update_turn_order_view(self):
        """
        --- FIX: Renamed from _redraw_tracker for clarity. ---
        This method now only calls the list update function.
        """
        current_combatant = self.model.get_current_combatant()
        current_id = current_combatant['id'] if current_combatant else None
        self.view.update_turn_order_list(self.model.turn_order, self.model.combatants, current_id, self)