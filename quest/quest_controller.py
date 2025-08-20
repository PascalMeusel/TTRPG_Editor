import customtkinter as ctk
from .quest_model import QuestModel
from .quest_view import QuestView, LinkSelectionDialog
from custom_dialogs import MessageBox
from character.character_model import CharacterModel
from npc.npc_model import NpcModel
from item.item_controller import ItemController

class QuestController:
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.model = QuestModel(campaign_path)
        self.view = QuestView(parent_frame)
        self.view.setup_ui(self)
        self.campaign_path = campaign_path
        self.all_quests = []
        self.selected_quest = None
        self.load_all_quests()

    def get_all_quests(self):
        """A simple getter for other controllers to access quest data."""
        return self.all_quests

    def load_all_quests(self):
        self.all_quests = self.model.load_all_quests()
        quests_by_status = {"Active": [], "Inactive": [], "Completed": [], "Failed": []}
        for quest in self.all_quests:
            status = quest.get('status', 'Inactive')
            if status in quests_by_status:
                quests_by_status[status].append(quest)
            else:
                quests_by_status["Inactive"].append(quest)
        self.view.display_quest_list(quests_by_status, self)
        if self.selected_quest:
            self.view.highlight_selected_quest(self.selected_quest['id'])
        else:
            self.view.highlight_selected_quest(None)
            self.view.clear_editor()

    def create_new_quest(self):
        dialog = ctk.CTkInputDialog(text="Enter the name for the new quest:", title="New Quest")
        title = dialog.get_input()
        if not title: return
        new_quest = self.model.create_quest(title)
        self.all_quests.append(new_quest)
        self.model.save_all_quests(self.all_quests)
        self.load_all_quests()
        self.select_quest(new_quest)

    def select_quest(self, quest):
        self.selected_quest = quest
        if not self.view.editor_is_built:
            self.view.build_quest_editor(self)
        self.view.populate_editor(quest)
        self.redraw_all_dynamic_content()
        self.view.highlight_selected_quest(quest['id'])

    def redraw_all_dynamic_content(self):
        if not self.selected_quest: return
        self.view.redraw_objectives(self.selected_quest['objectives'], self)
        self.redraw_links()
    
    def save_changes(self):
        if not self.selected_quest: return
        original_title = self.selected_quest['title']
        original_status = self.selected_quest['status']
        for quest in self.all_quests:
            if quest['id'] == self.selected_quest['id']:
                quest['title'] = self.view.title_entry.get()
                quest['status'] = self.view.status_combo.get()
                quest['description'] = self.view.desc_text.get("1.0", "end-1c")
                break
        self.model.save_all_quests(self.all_quests)
        if original_title != quest['title'] or original_status != quest['status']:
            self.load_all_quests()
        MessageBox.showinfo("Success", "Quest changes have been saved.", self.view.frame)

    def delete_quest(self):
        if not self.selected_quest: return
        if MessageBox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete '{self.selected_quest['title']}'?", self.view.frame):
            self.all_quests = [q for q in self.all_quests if q['id'] != self.selected_quest['id']]
            self.model.save_all_quests(self.all_quests)
            self.selected_quest = None
            self.load_all_quests()
            self.view.clear_editor()

    def add_objective(self):
        if not self.selected_quest: return
        self.selected_quest['objectives'].append({"text": "New Objective", "completed": False})
        self.view.redraw_objectives(self.selected_quest['objectives'], self)

    def remove_objective(self, index):
        if not self.selected_quest: return
        self.selected_quest['objectives'].pop(index)
        self.view.redraw_objectives(self.selected_quest['objectives'], self)
    
    def toggle_objective(self, index):
        if not self.selected_quest: return
        self.selected_quest['objectives'][index]['completed'] = not self.selected_quest['objectives'][index]['completed']
    
    def update_objective_text(self, index, new_text):
        if not self.selected_quest: return
        self.selected_quest['objectives'][index]['text'] = new_text

    def redraw_links(self):
        item_controller = self.app_controller.get_loaded_controller(ItemController)
        all_npcs_data = []
        if self.app_controller.ruleset_data:
            npc_names = NpcModel.get_for_ruleset(self.campaign_path, self.app_controller.ruleset_data['name'])
            all_npcs_data = [npc.to_dict() for npc in [NpcModel.load(self.campaign_path, name) for name in npc_names] if npc]
            for npc in all_npcs_data:
                npc['id'] = npc['name']
        
        all_items_data = item_controller.all_items if item_controller else []
        self.view.redraw_links(self.selected_quest['linked_npcs'], self.selected_quest['linked_items'], all_npcs_data, all_items_data, self)

    def show_add_npc_dialog(self):
        if not self.app_controller.ruleset_data: return
        all_npcs_data = [npc.to_dict() for npc in [NpcModel.load(self.campaign_path, name) for name in NpcModel.get_for_ruleset(self.campaign_path, self.app_controller.ruleset_data['name'])] if npc]
        for npc in all_npcs_data: npc['id'] = npc['name']
        dialog = LinkSelectionDialog(self.view.frame, "Link NPC", all_npcs_data)
        npc_id = dialog.get_selection()
        if npc_id and npc_id not in self.selected_quest['linked_npcs']:
            self.selected_quest['linked_npcs'].append(npc_id)
            self.redraw_links()

    def show_add_item_dialog(self):
        item_controller = self.app_controller.get_loaded_controller(ItemController)
        if not item_controller: return
        dialog = LinkSelectionDialog(self.view.frame, "Link Item", item_controller.all_items)
        item_id = dialog.get_selection()
        if item_id and item_id not in self.selected_quest['linked_items']:
            self.selected_quest['linked_items'].append(item_id)
            self.redraw_links()

    def remove_link(self, link_type, item_id):
        if not self.selected_quest: return
        if link_type == "npc":
            self.selected_quest['linked_npcs'].remove(item_id)
        elif link_type == "item":
            self.selected_quest['linked_items'].remove(item_id)
        self.redraw_links()