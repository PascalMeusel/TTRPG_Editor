from tkinter import messagebox
from .npc_model import NpcModel
from .npc_view import NpcView

class NpcController:
    """Controller for the NPC feature, scoped to a specific campaign."""
    def __init__(self, app_controller, creator_tab, sheet_tab, campaign_path):
        self.app_controller = app_controller
        self.view = NpcView(creator_tab, sheet_tab)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.current_npc = None
        self.selected_npc_name = None
        self.view.setup_ui(self)

    def get_npc_list(self):
        """Returns a list of NPC names for the current rule set within the active campaign."""
        if self.current_rule_set:
            return NpcModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
        return []

    def handle_rule_set_load(self, rule_set):
        """Called by the AppController. This is where the one-time UI build happens."""
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        
        # Build the recyclable sheet UI now that we have the ruleset
        self.view.build_sheet_ui(rule_set, self)
        
        self.update_npc_management_list()
        self.update_npc_sheet_list()

    def update_npc_management_list(self):
        """Refreshes the list of existing NPCs in the manager panel."""
        self.selected_npc_name = None
        if self.current_rule_set:
            npcs = NpcModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
            self.view.update_npc_management_list(npcs)
        else:
            self.view.update_npc_management_list([])
            
    def update_npc_sheet_list(self):
        """Refreshes the dropdown list of NPCs on the sheet tab."""
        if self.current_rule_set:
            npcs = NpcModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
            self.view.update_npc_sheet_list(npcs)
        else:
            self.view.update_npc_sheet_list([])
        self.view.clear_sheet()
        self.current_npc = None

    def save_new_npc(self):
        """Saves a new NPC to the current campaign."""
        if not self.current_rule_set:
            messagebox.showerror("Error", "No rule set loaded.")
            return
        
        name = self.view.npc_name_entry.get()
        if not name:
            messagebox.showerror("Error", "NPC name is required.")
            return
        
        npc = NpcModel(self.campaign_path, name, self.current_rule_set['name'])
        for key, entry in self.view.npc_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']:
                npc.attributes[key] = value
            elif key in self.current_rule_set['skills']:
                npc.skills[key] = value
        
        npc.gm_notes = self.view.npc_notes_text.get("1.0", "end").strip()
        npc.loot = [item.strip() for item in self.view.npc_loot_text.get("1.0", "end").strip().split('\n') if item.strip()]
        npc.save()
        
        messagebox.showinfo("Success", f"NPC '{name}' saved.")
        self.app_controller.on_character_or_npc_list_changed()
        
        # Clear creator fields for next entry
        self.view.npc_name_entry.delete(0, 'end')
        self.view.npc_notes_text.delete("1.0", 'end')
        self.view.npc_loot_text.delete("1.0", 'end')
        for entry in self.view.npc_creator_entries.values():
            entry.delete(0, 'end')


    def on_npc_select(self, event):
        """Stores the name of the NPC clicked in the management list."""
        try:
            line_content = self.view.npc_management_list.get("current linestart", "current lineend").strip()
            if line_content:
                self.selected_npc_name = line_content
        except Exception:
            self.selected_npc_name = None
            return
        self.view.highlight_selection()

    def delete_selected_npc(self):
        """Deletes the NPC selected in the management list."""
        npc_name = self.selected_npc_name
        if not npc_name:
            messagebox.showerror("Error", "Please select an NPC from the list to delete.")
            return
            
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?"):
            if NpcModel.delete(self.campaign_path, npc_name):
                messagebox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.")
                self.selected_npc_name = None
                self.app_controller.on_character_or_npc_list_changed()
            else:
                messagebox.showerror("Error", f"Could not find file for NPC '{npc_name}'.")

    def load_npc_to_sheet(self):
        """Loads a selected NPC into the sheet view by populating the recycled UI."""
        npc_name = self.view.npc_sheet_list.get()
        if not npc_name or npc_name == "-":
            self.current_npc = None
            self.view.clear_sheet()
            return

        self.current_npc = NpcModel.load(self.campaign_path, npc_name)
        if not self.current_npc:
            messagebox.showerror("Error", f"Could not load NPC: {npc_name}")
            return
        
        self.view.display_sheet_data(self.current_npc)
        self.app_controller.set_dirty_flag(False)
        
    def save_npc_sheet(self):
        """Saves any changes made to the NPC currently loaded in the sheet view."""
        if not self.current_npc: return
        
        for key, entry in self.view.npc_sheet_entries.items():
            value = entry.get()
            if key in self.current_npc.attributes:
                self.current_npc.attributes[key] = value
            elif key in self.current_npc.skills:
                self.current_npc.skills[key] = value
                
        self.current_npc.gm_notes = self.view.sheet_notes_text.get("1.0", "end").strip()
        self.current_npc.loot = [item.strip() for item in self.view.sheet_loot_text.get("1.0", "end").strip().split('\n') if item.strip()]
        
        self.current_npc.save()
        self.app_controller.set_dirty_flag(False)
        messagebox.showinfo("Success", f"Changes to '{self.current_npc.name}' saved.")

    def delete_current_npc(self):
        """Deletes the NPC currently loaded in the sheet view."""
        if not self.current_npc: return
        
        npc_name = self.current_npc.name
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?"):
            if NpcModel.delete(self.campaign_path, npc_name):
                messagebox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.")
                self.current_npc = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
                self.app_controller.set_dirty_flag(False)
            else:
                messagebox.showerror("Error", f"Could not find file for NPC '{npc_name}'.")
                
    def mark_as_dirty(self, event=None):
        """Notifies the AppController that there are unsaved changes."""
        self.app_controller.set_dirty_flag(True)