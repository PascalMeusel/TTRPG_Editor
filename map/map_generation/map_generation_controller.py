from .map_generation_view import MapGenerationDialog
from .map_generation_model import MapGenerationModel
from custom_dialogs import MessageBox # Ensure you have this file

class MapGenerationController:
    """Orchestrates the map generation process."""
    def __init__(self, parent_view):
        self.parent_view = parent_view
        self.model = MapGenerationModel()
        self.generated_data = None

    def show_generation_dialog(self):
        """Shows the generation dialog and returns the generated map data."""
        dialog = MapGenerationDialog(self.parent_view, self)
        user_input = dialog.get_result()

        if user_input:
            gen_type = user_input["gen_type"]
            settings = user_input["settings"]
            
            # Call the model to get the map data
            self.generated_data = self.model.generate(gen_type, settings)
            
            # Attach the common settings to the top level of the data
            self.generated_data['width'] = settings['width']
            self.generated_data['height'] = settings['height']
            self.generated_data['grid_scale'] = settings['grid_scale']
            
            return self.generated_data
        
        return None