from custom_dialogs import MessageBox
from .rules_model import RulesModel

class RulesController:
    """
    Controller for the Rules feature. 
    It can act as a simple data provider for the main app,
    or as a logic handler for the standalone editor window.
    """
    def __init__(self, app_controller):
        self.app_controller = app_controller
        self.model = RulesModel()
        self.view = None # This will be set for the standalone editor

    def set_view(self, view):
        """Connects this controller to the standalone editor view."""
        self.view = view

    def save_new_rule_set(self):
        """Saves a new rule set. This is ONLY called from the standalone window."""
        if not self.view:
            print("Error: Save function called without a view.")
            return

        name = self.view.rules_name_entry.get()
        if not name:
            MessageBox.showerror("Error", "Rule set name is required.", parent=self.view)
            return
        
        attrs = [attr.strip() for attr in self.view.rules_attrs_entry.get().split(',') if attr.strip()]
        skills_raw = self.view.rules_skills_text.get("1.0", "end").strip().split('\n')
        skills = {s.split(':')[0].strip(): s.split(':')[1].strip() for s in skills_raw if ':' in s}
        formulas_raw = self.view.rules_formulas_text.get("1.0", "end").strip().split('\n')
        formulas = {f.split(':')[0].strip(): f.split(':')[1].strip() for f in formulas_raw if ':' in f}

        self.model.save_rule_set(name, attrs, skills, formulas)
        MessageBox.showinfo("Success", f"Rule set '{name}' saved.", parent=self.view)