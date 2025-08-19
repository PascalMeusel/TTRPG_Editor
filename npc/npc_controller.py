from tkinter import messagebox
from .npc_model import NpcModel
from .npc_view import NpcView
from custom_dialogs import MessageBox
from character.character_view import AddItemDialog
from item.item_controller import ItemController
from .npc_generator_model import NpcGeneratorModel

class NpcController:
    """Controller for the self-contained NPC feature."""
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.view = NpcView(parent_frame)
        self.campaign_path = campaign_path
        self.current_rule_set = None
        self.current_npc = None
        self.generated_npc_data = None
        self.view.setup_ui(self)

    def get_item_controller(self):
        return self.app_controller.get_loaded_controller(ItemController)

    def get_npc_list(self):
        if self.current_rule_set:
            return NpcModel.get_for_ruleset(self.campaign_path, self.current_rule_set['name'])
        return []

    def handle_rule_set_load(self, rule_set):
        self.current_rule_set = rule_set
        self.view.build_dynamic_fields(rule_set)
        self.view.build_sheet_ui(rule_set, self)
        self.update_npc_management_list()
        self.update_npc_sheet_list()

    def update_npc_management_list(self):
        if self.current_rule_set:
            npcs = self.get_npc_list()
            self.view.update_npc_management_list(npcs)
        else:
            self.view.update_npc_management_list([])
            
    def update_npc_sheet_list(self):
        if self.current_rule_set:
            npcs = self.get_npc_list()
            self.view.update_npc_sheet_list(npcs)
        else:
            self.view.update_npc_sheet_list([])
        self.view.clear_sheet()
        self.current_npc = None

    def generate_random_npc(self):
        if not self.current_rule_set:
            MessageBox.showerror("Error", "A rule set must be loaded to generate an NPC.", self.view.parent_frame)
            return
        item_controller = self.get_item_controller()
        if not item_controller:
            MessageBox.showerror("Error", "The Item Editor must be open to generate items.", self.view.parent_frame)
            return
        generator = NpcGeneratorModel()
        npc_data = generator.generate(self.current_rule_set)
        created_items = []
        all_item_names = [item['name'].lower() for item in item_controller.all_items]
        for item_to_create_data in npc_data["items_to_create"]:
            if item_to_create_data["name"].lower() not in all_item_names:
                new_item = item_controller.create_item_from_data(item_to_create_data)
                created_items.append(new_item)
            else:
                for item in item_controller.all_items:
                    if item['name'].lower() == item_to_create_data['name'].lower():
                        created_items.append(item)
                        break
        item_controller.load_all_items()
        self.generated_npc_data = npc_data
        self.generated_npc_data['created_items'] = created_items
        self.view.populate_creator_fields(npc_data)
        MessageBox.showinfo("NPC Generated", f"Generated a new {npc_data['name']}! Review and save when ready.", self.view.parent_frame)

    def save_new_npc(self):
        if not self.current_rule_set:
            MessageBox.showerror("Error", "No rule set loaded.", self.view.parent_frame)
            return
        name = self.view.npc_name_entry.get()
        if not name:
            MessageBox.showerror("Error", "NPC name is required.", self.view.parent_frame)
            return
        npc = NpcModel(self.campaign_path, name, self.current_rule_set['name'])
        for key, entry in self.view.npc_creator_entries.items():
            value = entry.get() or "0"
            if key in self.current_rule_set['attributes']:
                npc.attributes[key] = value
            elif key in self.current_rule_set['skills']:
                npc.skills[key] = value
        
        npc.current_hp = npc.attributes.get("Hit Points", "10")
        npc.gm_notes = self.view.npc_notes_text.get("1.0", "end-1c")
        
        if self.generated_npc_data and self.generated_npc_data["name"] == name:
            for item in self.generated_npc_data.get("created_items", []):
                npc.inventory.append({"item_id": item["id"], "quantity": 1, "equipped": True})
        
        npc.save()
        MessageBox.showinfo("Success", f"NPC '{name}' saved.", self.view.parent_frame)
        self.app_controller.on_character_or_npc_list_changed()
        self.view.clear_creator_fields()
        self.generated_npc_data = None

    def delete_selected_npc(self):
        npc_name = self.view.npc_management_list.get().strip()
        if not npc_name or npc_name == "-":
            MessageBox.showerror("Error", "Please select an NPC from the list to delete.", self.view.parent_frame)
            return
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?", self.view.parent_frame):
            if NpcModel.delete(self.campaign_path, npc_name):
                MessageBox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.", self.view.parent_frame)
                self.app_controller.on_character_or_npc_list_changed()
            else:
                MessageBox.showerror("Error", f"Could not find file for NPC '{npc_name}'.", self.view.parent_frame)

    def load_npc_to_sheet(self, refresh=False):
        item_controller = self.get_item_controller()
        if not item_controller:
            MessageBox.showerror("Error", "The Item Editor must be open to manage inventory.", self.view.parent_frame)
            return
        npc_name = self.current_npc.name if (refresh and self.current_npc) else self.view.npc_sheet_list.get().strip()
        if not npc_name or npc_name == "-":
            self.current_npc = None
            self.view.clear_sheet()
            return
        self.current_npc = NpcModel.load(self.campaign_path, npc_name)
        if not self.current_npc:
            MessageBox.showerror("Error", f"Could not load NPC: {npc_name}", self.view.parent_frame)
            return
        self.view.display_sheet_data(self.current_npc, item_controller, self)
        if not refresh:
            self.app_controller.set_dirty_flag(False)
        
    def save_npc_sheet(self):
        if not self.current_npc: return
        
        self.current_npc.current_hp = self.view.current_hp_entry.get()
        
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
        MessageBox.showinfo("Success", f"Changes to '{self.current_npc.name}' saved.", self.view.parent_frame)

    def delete_current_npc(self):
        if not self.current_npc: return
        npc_name = self.current_npc.name
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete {npc_name}?", self.view.parent_frame):
            if NpcModel.delete(self.campaign_path, npc_name):
                MessageBox.showinfo("Deleted", f"NPC '{npc_name}' has been deleted.", self.view.parent_frame)
                self.current_npc = None
                self.view.clear_sheet()
                self.app_controller.on_character_or_npc_list_changed()
                self.app_controller.set_dirty_flag(False)
            else:
                MessageBox.showerror("Error", f"Could not find file for NPC '{npc_name}'.", self.view.parent_frame)

    def show_add_item_dialog(self):
        if not self.current_npc: return
        item_controller = self.get_item_controller()
        if not item_controller:
            MessageBox.showerror("Error", "The Item Editor must be open to add items.", self.view.parent_frame)
            return
        dialog = AddItemDialog(parent=self.view.parent_frame, all_items=item_controller.all_items)
        selected_item = dialog.get_selection()
        if selected_item:
            self.add_item_to_inventory(selected_item)

    def add_item_to_inventory(self, item_to_add):
        if not self.current_npc: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for inv_entry in self.current_npc.inventory:
            if inv_entry["item_id"] == item_to_add["id"]:
                inv_entry["quantity"] += 1
                break
        else:
            self.current_npc.inventory.append({"item_id": item_to_add["id"], "quantity": 1, "equipped": False})
        self.view.display_sheet_data(self.current_npc, item_controller, self)
        self.mark_as_dirty()

    def remove_item_from_inventory(self, inv_entry_to_remove):
        if not self.current_npc: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for i, inv_entry in enumerate(self.current_npc.inventory):
            if inv_entry["item_id"] == inv_entry_to_remove["item_id"]:
                inv_entry["quantity"] -= 1
                if inv_entry["quantity"] <= 0:
                    self.current_npc.inventory.pop(i)
                break
        self.view.display_sheet_data(self.current_npc, item_controller, self)
        self.mark_as_dirty()

    def toggle_item_equipped(self, inv_entry_to_toggle):
        if not self.current_npc: return
        item_controller = self.get_item_controller()
        if not item_controller: return
        for inv_entry in self.current_npc.inventory:
            if inv_entry["item_id"] == inv_entry_to_toggle["item_id"]:
                inv_entry["equipped"] = not inv_entry.get("equipped", False)
                break
        self.view.display_sheet_data(self.current_npc, item_controller, self)
        self.mark_as_dirty()
                
    def mark_as_dirty(self, event=None):
        self.app_controller.set_dirty_flag(True)