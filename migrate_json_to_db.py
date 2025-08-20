import os
import json
import uuid
import shutil

# We need to import the database and model classes from your project
from database import Database
from campaign_model import CampaignModel
from character.character_model import CharacterModel
from npc.npc_model import NpcModel
from item.item_model import ItemModel
from quest.quest_model import QuestModel

def migrate_characters(campaign_path, ruleset_name, db):
    """Migrates character data from individual JSON files to the database."""
    char_dir = os.path.join(campaign_path, 'characters')
    if not os.path.exists(char_dir):
        return

    # Check if the table is already populated
    db.connect()
    count = db.fetchone("SELECT COUNT(*) FROM characters")[0]
    db.close()
    if count > 0:
        print(f"    - Skipping characters: table already contains {count} entries.")
        return

    migrated_count = 0
    for filename in os.listdir(char_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(char_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Add missing fields for compatibility
                data['rule_set'] = ruleset_name
                if 'current_hp' not in data:
                    data['current_hp'] = data.get('attributes', {}).get('Hit Points', '10')

                char = CharacterModel.from_dict(campaign_path, data)
                char.save()
                migrated_count += 1
                
                # Rename file to prevent re-migration
                shutil.move(file_path, file_path + '.migrated')

            except Exception as e:
                print(f"      [ERROR] Could not migrate character {filename}: {e}")
    
    if migrated_count > 0:
        print(f"    - Migrated {migrated_count} characters successfully.")

def migrate_npcs(campaign_path, ruleset_name, db):
    """Migrates NPC data from individual JSON files to the database."""
    npc_dir = os.path.join(campaign_path, 'npcs')
    if not os.path.exists(npc_dir):
        return

    db.connect()
    count = db.fetchone("SELECT COUNT(*) FROM npcs")[0]
    db.close()
    if count > 0:
        print(f"    - Skipping NPCs: table already contains {count} entries.")
        return
        
    migrated_count = 0
    for filename in os.listdir(npc_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(npc_dir, filename)
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)

                data['rule_set'] = ruleset_name
                if 'current_hp' not in data:
                    data['current_hp'] = data.get('attributes', {}).get('Hit Points', '10')

                npc = NpcModel.from_dict(campaign_path, data)
                npc.save()
                migrated_count += 1
                shutil.move(file_path, file_path + '.migrated')
                
            except Exception as e:
                print(f"      [ERROR] Could not migrate NPC {filename}: {e}")

    if migrated_count > 0:
        print(f"    - Migrated {migrated_count} NPCs successfully.")

def migrate_items(campaign_path, db):
    """Migrates item data from items.json to the database."""
    item_file = os.path.join(campaign_path, 'items.json')
    # Handle the alternate location seen in the HelloWorld campaign
    if not os.path.exists(item_file):
        item_file = os.path.join(campaign_path, 'data', 'items.json')

    if not os.path.exists(item_file):
        return

    db.connect()
    count = db.fetchone("SELECT COUNT(*) FROM items")[0]
    db.close()
    if count > 0:
        print(f"    - Skipping items: table already contains {count} entries.")
        return

    migrated_count = 0
    try:
        with open(item_file, 'r') as f:
            items_data = json.load(f)
        
        item_model = ItemModel(campaign_path)
        for item_dict in items_data:
            # Ensure a unique ID exists
            if 'id' not in item_dict:
                item_dict['id'] = str(uuid.uuid4())
            item_model.save_item(item_dict)
            migrated_count += 1
        
        shutil.move(item_file, item_file + '.migrated')
        if migrated_count > 0:
            print(f"    - Migrated {migrated_count} items successfully.")

    except Exception as e:
        print(f"      [ERROR] Could not migrate items from {item_file}: {e}")

def migrate_quests(campaign_path, db):
    """Migrates quest data from quests.json to the database."""
    quest_file = os.path.join(campaign_path, 'quests.json')
    if not os.path.exists(quest_file):
        return
    
    db.connect()
    count = db.fetchone("SELECT COUNT(*) FROM quests")[0]
    db.close()
    if count > 0:
        print(f"    - Skipping quests: table already contains {count} entries.")
        return

    migrated_count = 0
    try:
        with open(quest_file, 'r') as f:
            quests_data = json.load(f)
            
        quest_model = QuestModel(campaign_path)
        for quest_dict in quests_data:
            if 'id' not in quest_dict:
                quest_dict['id'] = str(uuid.uuid4())
            quest_model.save_quest(quest_dict)
            migrated_count += 1
            
        shutil.move(quest_file, quest_file + '.migrated')
        if migrated_count > 0:
            print(f"    - Migrated {migrated_count} quests successfully.")
            
    except Exception as e:
        print(f"      [ERROR] Could not migrate quests from {quest_file}: {e}")

def run_migration():
    """Main function to find all campaigns and run the migration process."""
    print("="*50)
    print("Starting TTRPG Editor Data Migration")
    print("="*50)
    
    campaign_model = CampaignModel()
    all_campaigns = campaign_model.list_campaigns()
    
    if not all_campaigns:
        print("No campaigns found to migrate.")
        return
        
    for campaign_name in all_campaigns:
        print(f"\nProcessing Campaign: '{campaign_name}'")
        campaign_path = os.path.join(campaign_model.base_dir, campaign_name)
        
        # Ensure a database file exists, creating it if necessary.
        db = Database(campaign_path)
        db.connect()
        db.close()
        
        ruleset_name = campaign_model.get_campaign_ruleset(campaign_name)
        if not ruleset_name:
            print(f"  [WARNING] Could not find ruleset for '{campaign_name}'. Skipping character/NPC migration.")
        else:
            migrate_characters(campaign_path, ruleset_name, db)
            migrate_npcs(campaign_path, ruleset_name, db)
            
        migrate_items(campaign_path, db)
        migrate_quests(campaign_path, db)

    print("\n" + "="*50)
    print("Migration process finished.")
    print("Old .json files have been renamed to .migrated to prevent duplicates.")
    print("="*50)

if __name__ == "__main__":
    run_migration()