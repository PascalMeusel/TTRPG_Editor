from tkinter import messagebox
from .combat_model import CombatModel
from .combat_view import CombatView
from character.character_model import CharacterModel
from npc.npc_model import NpcModel

class CombatController:
    """Controller for the Combat Simulator feature within a specific campaign."""
    def __init__(self, app_controller, tab_frame, campaign_path):
        self.app_controller = app_controller
        self.model = CombatModel()
        self.view = CombatView(tab_frame)
        self.campaign_path = campaign_path # Store the active campaign path
        self.current_rule_set = None
        self.view.setup_ui(self)

    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.view.show_simulator(self)
        self.update_combatant_lists()

    def update_combatant_lists(self):
        if not self.current_rule_set: return
        rule_set_name = self.current_rule_set['name']
        
        # Use the campaign path to get the correct characters and NPCs
        chars = [f"PC: {name}" for name in CharacterModel.get_for_ruleset(self.campaign_path, rule_set_name)]
        npcs = [f"NPC: {name}" for name in NpcModel.get_for_ruleset(self.campaign_path, rule_set_name)]
        
        combatants = sorted(chars + npcs)
        self.view.update_combatant_lists(combatants)

    def _get_combatant_from_selection(self, selection_str):
        """Loads a Character or NPC model from the active campaign."""
        if not selection_str or selection_str == "-": return None, "No combatant selected."
        try:
            c_type, c_name = selection_str.split(': ', 1)
            if c_type == 'PC':
                return (CharacterModel.load(self.campaign_path, c_name), None)
            elif c_type == 'NPC':
                return (NpcModel.load(self.campaign_path, c_name), None)
            else:
                return None, "Invalid combatant type."
        except Exception as e:
            return None, f"Error loading combatant: {e}"

    def run_combat_hit(self):
        attacker, err = self._get_combatant_from_selection(self.view.attacker_list.get())
        if err: messagebox.showerror("Error", err); return
        defender, err = self._get_combatant_from_selection(self.view.defender_list.get())
        if err: messagebox.showerror("Error", err); return
        
        try:
            roll = int(self.view.roll_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Dice Roll must be a number."); return
            
        result_text, _ = self.model.check_hit(attacker, defender, roll, self.current_rule_set)
        self.view.write_to_log(f"{attacker.name} attacks {defender.name} (Roll: {roll})...\n> {result_text}")

    def run_combat_damage(self):
        attacker, err = self._get_combatant_from_selection(self.view.attacker_list.get())
        if err: messagebox.showerror("Error", err); return
        defender, err = self._get_combatant_from_selection(self.view.defender_list.get())
        if err: messagebox.showerror("Error", err); return
        
        try:
            roll = int(self.view.roll_entry.get())
            modifier = int(self.view.mod_entry.get())
        except (ValueError, TypeError):
            messagebox.showerror("Error", "Dice Roll and Modifier must be numbers."); return
            
        result_text, _ = self.model.calculate_damage(attacker, defender, roll, modifier)
        self.view.write_to_log(result_text)
        self.view.write_to_log(f"--> Reminder: Manually update {defender.name}'s Hit Points on their sheet.")