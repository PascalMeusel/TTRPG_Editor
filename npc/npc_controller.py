from tkinter import messagebox
from .npc_model import NpcModel
from .npc_view import NpcView
from custom_dialogs import MessageBox
from character.character_view import AddItemDialog

class NpcController:
    """Controller for the NPC feature, scoped to a specific campaign."""
    def __init__(self, app_controller, creator_tab, sheet_tab, campaign_path, item_controller):
        self.app_controller = app_controller
        self.item_controller = item_controller
        self.view = NpcView(creator_tab, sheet_tab)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.current_npc = None
        self.selected_npc_name = None
        self.view.setup_ui(self)

    def get_npc_list(self):
        """Returns a list of NPC names for the current rule set."""
        if self.current_rule_set:
            return NpcModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
        return []

    def handle_rule_set_load(self, rule_set):
        """Called by the AppController. Builds dynamic UI parts."""
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
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
            MessageBox.showerror("Error", "No rule set loaded.", self.view.creator_tab)
            return
        
        name = self.view.npc_name_entry.get()
        if not name:
            MessageBox.showerror("Error", "NPC name is required.", self.view.creator_tab)
            return
        
        npc = NpcModel(self.campaign_path, name, self.current_rule_set['name'])
        for key, entry in self.view.npc_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']:
                npc.attributes[key] = value
            elif key in self.current_rule_set['skills']:
                npc.skills[key] = value
        
        npc.gm_notes = self.view.npc_notes_text.get("1.0", "end-1c")
        npc.save()
        
        MessageBox.showinfo("Success", f"NPC '{name}' saved.", self.view.creator_tab)
        self.app_controller.on_character_or_npc_list_changed()
        
        self.view.npc_name_entry.delete(0, 'end')
        self.view.npc_notes_text.delete("1.0", 'end')
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
            MessageBox.showerror("Error", "Please select an NPC from the list to delete.", self.view.creator_tab)
            return
            
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?", self.view.creator_tab):
            if NpcModel.delete(self.campaign_path, npc_name):
                MessageBox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.", self.view.creator_tab)
                self.selected_npc_name = None
                self.app_controller.on_character_or_npc_list_changed()
            else:
                MessageBox.showerror("Error", f"Could not find file for NPC '{npc_name}'.", self.view.creator_tab)

    def load_npc_to_sheet(self):
        """Loads a selected NPC into the sheet view."""
        npc_name = self.view.npc_sheet_list.get()
        if not npc_name or npc_name == "-":
            self.current_npc = None
            self.view.clear_sheet()
            return

        self.current_npc = NpcModel.load(self.campaign_path, npc_name)
        if not self.current_npc:
            MessageBox.showerror("Error", f"Could not load NPC: {npc_name}", self.view.sheet_tab)
            return
        
        self.view.display_sheet_data(self.current_npc, self.item_controller)
        self.app_controller.set_dirty_flag(False)
        
    def save_npc_sheet(self):
        """Saves any changes made to the NPC currently loaded in the sheet view."""
        if not self.current_npc: return
        
        for key, entry in self.view.npc_sheet_entries.items():
            full_value = entry.get()
            if "(" in full_value and full_value.endswith(")"):
                base_value = full_value.split('(')[-1].strip(')')
            else:
                base_value = full_value
            
            if key in self.current_npc.attributes:
                self.current_npc.attributes[key] = base_value
            elif key in self.current_npc.skills:
                self.current_npc.skills[key] = base_value
                
        self.current_npc.gm_notes = self.view.sheet_notes_text.get("1.0", "end-1c")
        self.current_npc.save()
        self.app_controller.set_dirty_flag(False)
        MessageBox.showinfo("Success", f"Changes to '{self.current_npc.name}' saved.", self.view.sheet_tab)

    def delete_current_npc(self):
        """Deletes the NPC currently loaded in the sheet view."""
        if not self.current_npc: return
        npc_name = self.current_npc.name
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?", self.view.sheet_tab):
            if NpcModel.delete(self.campaign_path, npc_name):
                MessageBox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.", self.view.sheet_tab)
                self.current_npc = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
                self.app_controller.set_dirty_flag(False)
            else:
                MessageBox.showerror("Error", f"Could not find file for NPC '{npc_name}'.", self.view.sheet_tab)

    def show_add_item_dialog(self):
        """Opens the dialog to add an item to the current NPC's inventory."""
        if not self.current_npc: return
        
        dialog = AddItemDialog(parent=self.view.sheet_tab, all_items=self.item_controller.all_items)
        selected_item = dialog.get_selection()
        
        if selected_item:
            self.add_item_to_inventory(selected_item)

    def add_item_to_inventory(self, item_to_add):
        """Adds a given item to the current NPC's model."""
        if not self.current_npc: return
        
        for inv_entry in self.current_npc.inventory:
            if inv_entry["item_id"] == item_to_add["id"]:
                inv_entry["quantity"] += 1
                break
        else:
            self.current_npc.inventory.append({
                "item_id": item_to_add["id"], 
                "quantity": 1,
                "equipped": False
            })
        
        self.view.display_sheet_data(self.current_npc, self.item_controller)
        self.mark_as_dirty()

    def remove_item_from_inventory(self, inv_entry_to_remove):
        """Removes a given item entry from the current NPC's model."""
        if not self.current_npc: return
        
        for i, inv_entry in enumerate(self.current_npc.inventory):
            if inv_entry["item_id"] == inv_entry_to_remove["item_id"]:
                inv_entry["quantity"] -= 1
                if inv_entry["quantity"] <= 0:
                    self.current_npc.inventory.pop(i)
                break

        self.view.display_sheet_data(self.current_npc, self.item_controller)
        self.mark_as_dirty()

    def toggle_item_equipped(self, inv_entry_to_toggle):
        """Finds an item in the inventory and flips its 'equipped' status."""
        if not self.current_npc: return

        for inv_entry in self.current_npc.inventory:
            if inv_entry["item_id"] == inv_entry_to_toggle["item_id"]:
                inv_entry["equipped"] = not inv_entry.get("equipped", False)
                break
        
        self.view.display_sheet_data(self.current_npc, self.item_controller)
        self.mark_as_dirty()
                
    def mark_as_dirty(self, event=None):
        """Notifies the AppController that there are unsaved changes."""
        self.app_controller.set_dirty_flag(True)