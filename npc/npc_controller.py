from tkinter import messagebox
from .npc_model import NpcModel
from .npc_view import NpcView

class NpcController:
    """Controller for the NPC feature."""
    def __init__(self, app_controller, creator_tab, sheet_tab):
        self.app_controller = app_controller
        self.view = NpcView(creator_tab, sheet_tab)
        self.current_rule_set = None
        self.current_npc = None # The NPC loaded in the sheet view
        self.selected_npc_name = None # For deletion from the management list
        self.view.setup_ui(self)

    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        self.update_npc_management_list()
        self.update_npc_sheet_list()

    def save_new_npc(self):
        if not self.current_rule_set: messagebox.showerror("Error", "Please load a rule set first."); return
        name = self.view.npc_name_entry.get()
        if not name: messagebox.showerror("Error", "NPC name is required."); return
        
        npc = NpcModel(name, self.current_rule_set['name'])
        for key, entry in self.view.npc_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']: npc.attributes[key] = value
            elif key in self.current_rule_set['skills']: npc.skills[key] = value
        
        npc.gm_notes = self.view.npc_notes_text.get("1.0", "end").strip()
        npc.loot = [item.strip() for item in self.view.npc_loot_text.get("1.0", "end").strip().split('\n') if item.strip()]
        npc.save()
        messagebox.showinfo("Success", f"NPC '{name}' saved.")
        self.app_controller.on_character_or_npc_list_changed()

    def on_npc_select(self, event):
        try:
            line_content = self.view.npc_management_list.get("current linestart", "current lineend").strip()
            if line_content: self.selected_npc_name = line_content
        except Exception: self.selected_npc_name = None; return
        self.view.highlight_selection()

    def delete_selected_npc(self):
        npc_name = self.selected_npc_name
        if not npc_name:
            messagebox.showerror("Error", "Please select an NPC from the list to delete.")
            return
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?"):
            if NpcModel.delete(npc_name):
                messagebox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.")
                self.selected_npc_name = None
                self.app_controller.on_character_or_npc_list_changed()
            else:
                messagebox.showerror("Error", f"Could not find file for NPC '{npc_name}'.")

    def update_npc_management_list(self):
        self.selected_npc_name = None
        if self.current_rule_set:
            npcs = NpcModel.get_for_ruleset(self.current_rule_set['name'])
            self.view.update_npc_management_list(npcs)
        else:
            self.view.update_npc_management_list([])
            
    def update_npc_sheet_list(self):
        if self.current_rule_set:
            npcs = NpcModel.get_for_ruleset(self.current_rule_set['name'])
            self.view.update_npc_sheet_list(npcs)
        else:
            self.view.update_npc_sheet_list([])
        self.view.clear_sheet()
        self.current_npc = None

    def load_npc_to_sheet(self):
        self.view.clear_sheet()
        npc_name = self.view.npc_sheet_list.get()
        if not npc_name or npc_name == "-":
            self.current_npc = None
            return

        self.current_npc = NpcModel.load(npc_name)
        if not self.current_npc:
            messagebox.showerror("Error", f"Could not load NPC: {npc_name}")
            return
        
        self.view.display_sheet_data(self.current_npc, self)
        
    def save_npc_sheet(self):
        if not self.current_npc: return
        
        # Save attributes and skills
        for key, entry in self.view.npc_sheet_entries.items():
            value = entry.get()
            if key in self.current_npc.attributes: self.current_npc.attributes[key] = value
            elif key in self.current_npc.skills: self.current_npc.skills[key] = value
            
        # Save GM-specific fields
        self.current_npc.gm_notes = self.view.sheet_notes_text.get("1.0", "end").strip()
        self.current_npc.loot = [item.strip() for item in self.view.sheet_loot_text.get("1.0", "end").strip().split('\n') if item.strip()]
        
        self.current_npc.save()
        messagebox.showinfo("Success", f"Changes to '{self.current_npc.name}' saved.")

    def delete_current_npc(self):
        if not self.current_npc: return
        
        npc_name = self.current_npc.name
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?"):
            if NpcModel.delete(npc_name):
                messagebox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.")
                self.current_npc = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
            else:
                messagebox.showerror("Error", f"Could not find file for NPC '{npc_name}'.")
                # Add this method inside the NpcController class
    def get_npc_list(self):
        """Returns a list of NPC names for the current rule set."""
        if self.current_rule_set:
            return NpcModel.get_for_ruleset(self.current_rule_set['name'])
        return []