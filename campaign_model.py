import os
import json

class CampaignModel:
    """Manages the creation and listing of campaign save files."""
    def __init__(self, base_dir="data/campaigns"):
        self.base_dir = base_dir
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def list_campaigns(self):
        """Returns a list of all existing campaign names."""
        return sorted([d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))])

    def create_campaign(self, name, ruleset_name):
        """Creates the necessary directory structure for a new campaign."""
        campaign_path = os.path.join(self.base_dir, name)
        if os.path.exists(campaign_path):
            return None # Campaign already exists

        # Create all necessary subdirectories
        os.makedirs(os.path.join(campaign_path, "characters"))
        os.makedirs(os.path.join(campaign_path, "npcs"))
        os.makedirs(os.path.join(campaign_path, "maps"))

        # Create a metadata file to store the chosen ruleset
        metadata = {"ruleset": ruleset_name}
        with open(os.path.join(campaign_path, "campaign.json"), 'w') as f:
            json.dump(metadata, f, indent=4)
        
        return campaign_path

    def get_campaign_ruleset(self, name):
        """Reads the metadata file to find which ruleset a campaign uses."""
        metadata_path = os.path.join(self.base_dir, name, "campaign.json")
        if not os.path.exists(metadata_path):
            return None
        with open(metadata_path, 'r') as f:
            data = json.load(f)
            return data.get("ruleset")