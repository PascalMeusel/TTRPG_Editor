from tkinter import messagebox
from .character_model import CharacterModel
from .character_view import CharacterView, AddItemDialog
from custom_dialogs import MessageBox

class CharacterController:
    """Controller for the Character feature, scoped to a specific campaign."""
    def __init__(self, app_controller, creator_tab, sheet_tab, campaign_path, item_controller):
        self.app_controller = app_controller
        self.item_controller = item_controller
        self.view = CharacterView(creator_tab, sheet_tab)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.current_character = None
        self.view.setup_creator_ui(self)
        self.view.setup_sheet_ui(self)

    def get_character_list(self):
        """Returns a list of character names for the current rule set."""
        if self.current_rule_set:
            return CharacterModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
        return []

    def handle_rule_set_load(self, rule_set):
        """Called by the AppController. Builds dynamic UI parts."""
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        self.view.build_sheet_ui(rule_set, self)
        self.update_character_sheet_list()

    def update_character_sheet_list(self):
        """Refreshes the dropdown list of characters on the Character Sheet tab."""
        if self.current_rule_set:
            characters = CharacterModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
            self.view.update_character_list(characters)
        else:
            self.view.update_character_list([])
        self.view.clear_sheet()
        self.current_character = None

    def save_new_character(self):
        """Saves a new character to the current campaign."""
        if not self.current_rule_set:
            MessageBox.showerror("Error", "No rule set loaded.", self.view.creator_tab)
            return
        
        name = self.view.char_name_entry.get()
        if not name:
            MessageBox.showerror("Error", "Character name is required.", self.view.creator_tab)
            return
        
        char = CharacterModel(self.campaign_path, name, self.current_rule_set['name'])
        for key, entry in self.view.char_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']:
                char.set_attribute(key, value)
            elif key in self.current_rule_set['skills']:
                char.set_skill(key, value)
        
        char.save()
        MessageBox.showinfo("Success", f"Character '{name}' saved.", self.view.creator_tab)
        self.app_controller.on_character_or_npc_list_changed()
        self.view.char_name_entry.delete(0, 'end')
        for entry in self.view.char_creator_entries.values():
            entry.delete(0, 'end')

    def load_character_to_sheet(self):
        """Loads a selected character into the sheet view."""
        char_name = self.view.char_sheet_list.get()
        if not char_name or char_name == "-":
            self.current_character = None
            self.view.clear_sheet()
            return

        self.current_character = CharacterModel.load(self.campaign_path, char_name)
        if not self.current_character:
            MessageBox.showerror("Error", f"Could not load character: {char_name}", self.view.sheet_tab)
            return
            
        self.view.display_sheet_data(self.current_character, self.item_controller)
        self.app_controller.set_dirty_flag(False)

    def save_character_sheet(self):
        """Saves changes to the character currently loaded in the sheet view."""
        if not self.current_character: return
        
        for key, entry in self.view.char_sheet_entries.items():
            full_value = entry.get()
            # If the value is "Effective (Base)", parse out the base value
            if "(" in full_value and full_value.endswith(")"):
                base_value = full_value.split('(')[-1].strip(')')
            else:
                base_value = full_value

            if key in self.current_character.attributes:
                self.current_character.set_attribute(key, base_value)
            else:
                self.current_character.set_skill(key, base_value)
        
        self.current_character.save()
        self.app_controller.set_dirty_flag(False)
        MessageBox.showinfo("Success", f"Changes to '{self.current_character.name}' saved.", self.view.sheet_tab)

    def delete_current_character(self):
        """Deletes the character currently loaded in the sheet view."""
        if not self.current_character: return
        char_name = self.current_character.name
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {char_name}?", self.view.sheet_tab):
            if CharacterModel.delete(self.campaign_path, char_name):
                MessageBox.showinfo("Deleted", f"Character '{char_name}' has been deleted.", self.view.sheet_tab)
                self.current_character = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
                self.app_controller.set_dirty_flag(False)
            else:
                MessageBox.showerror("Error", f"Could not find file for character '{char_name}'.", self.view.sheet_tab)

    def show_add_item_dialog(self):
        """Opens the dialog to add an item to the current character's inventory."""
        if not self.current_character: return
        
        dialog = AddItemDialog(parent=self.view.sheet_tab, all_items=self.item_controller.all_items)
        selected_item = dialog.get_selection()
        
        if selected_item:
            self.add_item_to_inventory(selected_item)

    def add_item_to_inventory(self, item_to_add):
        """Adds a given item to the current character's model."""
        if not self.current_character: return
        
        for inv_entry in self.current_character.inventory:
            if inv_entry["item_id"] == item_to_add["id"]:
                inv_entry["quantity"] += 1
                break
        else:
            self.current_character.inventory.append({
                "item_id": item_to_add["id"], 
                "quantity": 1,
                "equipped": False 
            })
        
        self.view.display_sheet_data(self.current_character, self.item_controller)
        self.mark_as_dirty()

    def remove_item_from_inventory(self, inv_entry_to_remove):
        """Removes a given item entry from the current character's model."""
        if not self.current_character: return
        
        for i, inv_entry in enumerate(self.current_character.inventory):
            if inv_entry["item_id"] == inv_entry_to_remove["item_id"]:
                inv_entry["quantity"] -= 1
                if inv_entry["quantity"] <= 0:
                    self.current_character.inventory.pop(i)
                break

        self.view.display_sheet_data(self.current_character, self.item_controller)
        self.mark_as_dirty()

    def toggle_item_equipped(self, inv_entry_to_toggle):
        """Finds an item in the inventory and flips its 'equipped' status."""
        if not self.current_character: return

        for inv_entry in self.current_character.inventory:
            if inv_entry["item_id"] == inv_entry_to_toggle["item_id"]:
                inv_entry["equipped"] = not inv_entry.get("equipped", False)
                break
        
        self.view.display_sheet_data(self.current_character, self.item_controller)
        self.mark_as_dirty()

    def mark_as_dirty(self, event=None):
        """Notifies the AppController that there are unsaved changes."""
        self.app_controller.set_dirty_flag(True)