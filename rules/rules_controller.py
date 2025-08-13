from tkinter import messagebox
from .rules_model import RulesModel
from .rules_view import RulesView

class RulesController:
    """Controller for the Rules feature."""
    def __init__(self, app_controller, left_panel_frame, creation_tab_frame):
        self.app_controller = app_controller
        self.model = RulesModel()
        self.view = RulesView(left_panel_frame, creation_tab_frame)
        self.selected_rule_set_name = None
        self.view.setup_ui(self)
        self.populate_rule_set_list()
        
    def populate_rule_set_list(self):
        rule_sets = self.model.get_all_rule_sets()
        self.view.populate_rule_set_list(rule_sets)

    def on_rule_set_select(self, event):
        try:
            line_content = self.view.rule_set_listbox.get("current linestart", "current lineend").strip()
            if line_content: self.selected_rule_set_name = line_content
        except Exception: self.selected_rule_set_name = None; return
        self.view.highlight_selection()

    def load_selected_rule_set(self):
        rule_set_name = self.selected_rule_set_name
        if not rule_set_name:
            messagebox.showerror("Error", "Please select a rule set by clicking its name.")
            return
        
        rule_set_data = self.model.load_rule_set(rule_set_name)
        if rule_set_data:
            # Update the local status display
            self.view.update_status(rule_set_name)
            # Broadcast the load event to other controllers
            self.app_controller.on_rule_set_loaded(rule_set_data)
        else:
            messagebox.showerror("Error", "Failed to load rule set.")

    def save_new_rule_set(self):
        name = self.view.rules_name_entry.get()
        if not name: messagebox.showerror("Error", "Rule set name is required."); return
        
        attrs = [attr.strip() for attr in self.view.rules_attrs_entry.get().split(',') if attr.strip()]
        skills_raw = self.view.rules_skills_text.get("1.0", "end").strip().split('\n')
        skills = {s.split(':')[0].strip(): s.split(':')[1].strip() for s in skills_raw if ':' in s}
        formulas_raw = self.view.rules_formulas_text.get("1.0", "end").strip().split('\n')
        formulas = {f.split(':')[0].strip(): f.split(':')[1].strip() for f in formulas_raw if ':' in f}

        self.model.save_rule_set(name, attrs, skills, formulas)
        messagebox.showinfo("Success", f"Rule set '{name}' saved.")
        self.populate_rule_set_list()