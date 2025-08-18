from .item_model import ItemModel
from .item_view import ItemView
from custom_dialogs import MessageBox

class ItemController:
    """Controller for the self-contained Item feature."""
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.model = ItemModel(campaign_path)
        self.view = ItemView(parent_frame)
        self.view.setup_ui(self)

        self.all_items = []
        self.selected_item = None
        self.current_rule_set = None
        self.load_all_items()

    def handle_rule_set_load(self, rule_set):
        """Receives the loaded rule set and tells the view to build the modifier UI."""
        self.current_rule_set = rule_set
        self.view.build_modifier_fields(rule_set, self)

    def adjust_modifier(self, stat_name, delta):
        """Called by the +/- buttons to change a stat modifier's value."""
        if stat_name in self.view.modifier_widgets:
            label = self.view.modifier_widgets[stat_name]
            current_value = int(label.cget("text"))
            new_value = current_value + delta
            label.configure(text=str(new_value))

    def load_all_items(self):
        """Loads items from the model and tells the view to display them."""
        self.all_items = self.model.load_all_items()
        self.all_items.sort(key=lambda x: x['name'].lower())
        self.view.display_items(self.all_items, self)
        self.clear_editor_fields()

    def select_item(self, item):
        """Handles when a user clicks on an item in the list."""
        self.selected_item = item
        self.view.populate_editor(item)
        self.view.editor_label.configure(text=f"Editing: {item['name']}")

    def _get_modifiers_from_view(self):
        """Reads all non-zero modifier values from the dynamic UI."""
        modifiers = []
        if not self.current_rule_set:
            return modifiers

        for stat_name, value_label in self.view.modifier_widgets.items():
            value = int(value_label.cget("text"))
            if value != 0:
                modifiers.append({"stat": stat_name, "value": value})
        return modifiers

    def save_new_item(self):
        """Saves a brand new item."""
        name = self.view.name_entry.get()
        desc = self.view.desc_textbox.get("1.0", "end-1c")
        item_type = self.view.type_combo.get()

        if not name:
            MessageBox.showerror("Error", "Item name is required.", parent=self.view.parent_frame)
            return

        modifiers = self._get_modifiers_from_view()
        
        new_item = self.model.create_item(name, desc, item_type, modifiers)
        self.all_items.append(new_item)
        self.model.save_all_items(self.all_items)
        self.load_all_items()
        MessageBox.showinfo("Success", f"Item '{name}' created.", parent=self.view.parent_frame)

    def create_item_from_data(self, item_data):
        """Creates a new item from a dictionary, used by generators."""
        new_item = self.model.create_item(
            item_data["name"],
            item_data["description"],
            item_data["type"],
            item_data["modifiers"]
        )
        self.all_items.append(new_item)
        self.model.save_all_items(self.all_items)
        # Note: We don't call load_all_items() here to avoid multiple UI refreshes
        # The calling function (NPC controller) will handle the final UI refresh.
        return new_item

    def save_changes(self):
        """Saves changes to an existing, selected item."""
        if not self.selected_item:
            return

        new_name = self.view.name_entry.get()
        new_desc = self.view.desc_textbox.get("1.0", "end-1c")
        new_type = self.view.type_combo.get()

        if not new_name:
            MessageBox.showerror("Error", "Item name is required.", parent=self.view.parent_frame)
            return
            
        modifiers = self._get_modifiers_from_view()
        
        for item in self.all_items:
            if item["id"] == self.selected_item["id"]:
                item["name"] = new_name
                item["description"] = new_desc
                item["type"] = new_type
                item["modifiers"] = modifiers
                break
        
        self.model.save_all_items(self.all_items)
        self.load_all_items()
        MessageBox.showinfo("Success", f"Item '{new_name}' updated.", parent=self.view.parent_frame)

    def delete_item(self):
        """Deletes the currently selected item."""
        if not self.selected_item:
            return
            
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete '{self.selected_item['name']}'?", parent=self.view.parent_frame):
            self.all_items = [item for item in self.all_items if item["id"] != self.selected_item["id"]]
            self.model.save_all_items(self.all_items)
            self.load_all_items()
            MessageBox.showinfo("Deleted", "Item has been deleted.", parent=self.view.parent_frame)

    def clear_editor_fields(self):
        """Clears the selection and the editor fields."""
        self.selected_item = None
        self.view.clear_editor()