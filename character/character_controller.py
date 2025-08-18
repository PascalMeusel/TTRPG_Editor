from tkinter import messagebox
from .character_model import CharacterModel
from .character_view import CharacterView, AddItemDialog
from custom_dialogs import MessageBox
from item.item_controller import ItemController

class CharacterController:
    # ... (init and other methods are unchanged) ...
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.view = CharacterView(parent_frame)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.current_character = None
        self.view.setup_ui(self)
    def get_item_controller(self):
        return self.app_controller.get_loaded_controller(ItemController)
    def get_character_list(self):
        if self.current_rule_set:
            return CharacterModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
        return []
    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        self.view.build_sheet_ui(rule_set, self)
        self.update_character_sheet_list()
    def update_character_sheet_list(self):
        if self.current_rule_set:
            characters = self.get_character_list()
            self.view.update_character_list(characters)
        else:
            self.view.update_character_list([])
        self.view.clear_sheet()
        self.current_character = None
    def save_new_character(self):
        if not self.current_rule_set:
            MessageBox.showerror("Error", "No rule set loaded.", self.view.parent_frame)
            return
        name = self.view.char_name_entry.get()
        if not name:
            MessageBox.showerror("Error", "Character name is required.", self.view.parent_frame)
            return
        char = CharacterModel(self.campaign_path, name, self.current_rule_set['name'])
        for key, entry in self.view.char_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']:
                char.set_attribute(key, value)
            elif key in self.current_rule_set['skills']:
                char.set_skill(key, value)
        char.save()
        MessageBox.showinfo("Success", f"Character '{name}' saved.", self.view.parent_frame)
        self.app_controller.on_character_or_npc_list_changed()
        self.view.char_name_entry.delete(0, 'end')
        for entry in self.view.char_creator_entries.values():
            entry.delete(0, 'end')

    def load_character_to_sheet(self):
        item_controller = self.get_item_controller()
        if not item_controller:
            MessageBox.showerror("Error", "The Item Editor must be open in one of the panes to manage inventory.", self.view.parent_frame)
            return
        char_name = self.view.char_sheet_list.get()
        if not char_name or char_name == "-":
            self.current_character = None
            self.view.clear_sheet()
            return
        self.current_character = CharacterModel.load(self.campaign_path, char_name)
        if not self.current_character:
            MessageBox.showerror("Error", f"Could not load character: {char_name}", self.view.parent_frame)
            return
        
        # --- FIX: Pass the controller instance (self) to the view ---
        self.view.display_sheet_data(self.current_character, item_controller, self)
        self.app_controller.set_dirty_flag(False)

    def save_character_sheet(self):
        if not self.current_character: return
        for key, entry in self.view.char_sheet_entries.items():
            full_value = entry.get()
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
        MessageBox.showinfo("Success", f"Changes to '{self.current_character.name}' saved.", self.view.parent_frame)

    def delete_current_character(self):
        if not self.current_character: return
        char_name = self.current_character.name
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {char_name}?", self.view.parent_frame):
            if CharacterModel.delete(self.campaign_path, char_name):
                MessageBox.showinfo("Deleted", f"Character '{char_name}' has been deleted.", self.view.parent_frame)
                self.current_character = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
                self.app_controller.set_dirty_flag(False)
            else:
                MessageBox.showerror("Error", f"Could not find file for character '{char_name}'.", self.view.parent_frame)

    def show_add_item_dialog(self):
        if not self.current_character: return
        item_controller = self.get_item_controller()
        if not item_controller:
            MessageBox.showerror("Error", "The Item Editor must be open in one of the panes to add items.", self.view.parent_frame)
            return
        dialog = AddItemDialog(parent=self.view.parent_frame, all_items=item_controller.all_items)
        selected_item = dialog.get_selection()
        if selected_item:
            self.add_item_to_inventory(selected_item)

    def add_item_to_inventory(self, item_to_add):
        if not self.current_character: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for inv_entry in self.current_character.inventory:
            if inv_entry["item_id"] == item_to_add["id"]:
                inv_entry["quantity"] += 1
                break
        else:
            self.current_character.inventory.append({"item_id": item_to_add["id"], "quantity": 1, "equipped": False})
        self.view.display_sheet_data(self.current_character, item_controller, self)
        self.mark_as_dirty()

    def remove_item_from_inventory(self, inv_entry_to_remove):
        if not self.current_character: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for i, inv_entry in enumerate(self.current_character.inventory):
            if inv_entry["item_id"] == inv_entry_to_remove["item_id"]:
                inv_entry["quantity"] -= 1
                if inv_entry["quantity"] <= 0:
                    self.current_character.inventory.pop(i)
                break
        self.view.display_sheet_data(self.current_character, item_controller, self)
        self.mark_as_dirty()

    def toggle_item_equipped(self, inv_entry_to_toggle):
        if not self.current_character: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for inv_entry in self.current_character.inventory:
            if inv_entry["item_id"] == inv_entry_to_toggle["item_id"]:
                inv_entry["equipped"] = not inv_entry.get("equipped", False)
                break
        self.view.display_sheet_data(self.current_character, item_controller, self)
        self.mark_as_dirty()

    def mark_as_dirty(self, event=None):
        self.app_controller.set_dirty_flag(True)