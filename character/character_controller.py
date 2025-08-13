from tkinter import messagebox
from .character_model import CharacterModel
from .character_view import CharacterView

class CharacterController:
    """Controller for the Character feature."""
    def __init__(self, app_controller, creator_tab, sheet_tab):
        self.app_controller = app_controller
        self.view = CharacterView(creator_tab, sheet_tab)
        self.current_rule_set = None
        self.current_character = None
        self.view.setup_creator_ui(self)
        self.view.setup_sheet_ui(self)

    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        self.update_character_sheet_list()

    def update_character_sheet_list(self):
        if self.current_rule_set:
            characters = CharacterModel.get_for_ruleset(self.current_rule_set['name'])
            self.view.update_character_list(characters)
        else:
            self.view.update_character_list([])
        self.view.clear_sheet()

    def save_new_character(self):
        if not self.current_rule_set: messagebox.showerror("Error", "Please load a rule set first."); return
        name = self.view.char_name_entry.get()
        if not name: messagebox.showerror("Error", "Character name is required."); return
        
        char = CharacterModel(name, self.current_rule_set['name'])
        for key, entry in self.view.char_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']: char.set_attribute(key, value)
            elif key in self.current_rule_set['skills']: char.set_skill(key, value)
        
        char.save()
        messagebox.showinfo("Success", f"Character '{name}' saved.")
        self.app_controller.on_character_or_npc_list_changed()

    def load_character_to_sheet(self):
        self.view.clear_sheet()
        char_name = self.view.char_sheet_list.get()
        if not char_name or char_name == "-": return

        self.current_character = CharacterModel.load(char_name)
        if not self.current_character:
            messagebox.showerror("Error", f"Could not load character: {char_name}")
            return
        
        self.view.display_sheet_data(self.current_character, self)

    def save_character_sheet(self):
        if not self.current_character: return
        for key, entry in self.view.char_sheet_entries.items():
            value = entry.get()
            if key in self.current_character.attributes: self.current_character.set_attribute(key, value)
            else: self.current_character.set_skill(key, value)
        
        inv_text = self.view.inv_textbox.get("1.0", "end").strip()
        new_inventory = []
        if inv_text:
            for line in inv_text.split('\n'):
                if not line.strip(): continue
                parts = line.split(':', 1)
                new_inventory.append({"name": parts[0].strip(), "description": parts[1].strip() if len(parts) > 1 else ""})
        self.current_character.inventory = new_inventory
        self.current_character.save()
        messagebox.showinfo("Success", f"Changes to '{self.current_character.name}' saved.")

    def delete_current_character(self):
        if not self.current_character: return
        char_name = self.current_character.name
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {char_name}?"):
            if CharacterModel.delete(char_name):
                messagebox.showinfo("Deleted", f"Character '{char_name}' has been deleted.")
                self.current_character = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
            else:
                messagebox.showerror("Error", f"Could not find file for character '{char_name}'.")
                # Add this method inside the CharacterController class
    def get_character_list(self):
        """Returns a list of character names for the current rule set."""
        if self.current_rule_set:
            return CharacterModel.get_for_ruleset(self.current_rule_set['name'])
        return []