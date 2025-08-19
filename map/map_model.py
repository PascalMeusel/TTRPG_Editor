import json
import os
import random
import math

class MapModel:
    """Manages map data, supporting multiple levels and landmarks."""
    def __init__(self, campaign_path, name="New Map", width=50, height=50, grid_size=20, grid_scale=1.5):
        self.campaign_path = campaign_path
        self.name = name
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_scale = grid_scale
        
        self.map_type = "outside"
        # --- NEW: Add a 'landmarks' list to each level ---
        self.levels = {0: {'elements': [], 'tokens': [], 'landmarks': []}}
        
        self.maps_dir = os.path.join(self.campaign_path, 'maps')
        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)

    def clear_map_level(self, level_index=0):
        """Clears all elements, tokens, and landmarks from a specific level."""
        if level_index not in self.levels:
            self.levels[level_index] = {'elements': [], 'tokens': [], 'landmarks': []}
        else:
            self.levels[level_index]['elements'].clear()
            self.levels[level_index]['landmarks'].clear()
        
        self.add_element({'type': 'rect', 'coords': (0, 0, self.width, self.height), 'color': '#2B2B2B'}, level_index)


    def add_element(self, element, level_index=0):
        if level_index in self.levels:
            self.levels[level_index]['elements'].append(element)
    
    def add_landmark(self, x, y, text, level_index=0):
        """Adds a new landmark to the specified level."""
        if level_index in self.levels:
            self.levels[level_index]['landmarks'].append({'x': x, 'y': y, 'text': text})

    def add_token(self, name, token_type, x, y, level_index=0):
        if level_index not in self.levels: return False
        if any(t['name'] == name for t in self.get_all_tokens()): return False
        self.levels[level_index]['tokens'].append({'name': name, 'type': token_type, 'x': x, 'y': y})
        return True

    def delete_token(self, token_name, level_index=0):
        if level_index in self.levels:
            self.levels[level_index]['tokens'] = [t for t in self.levels[level_index]['tokens'] if t.get('name') != token_name]

    def move_token(self, token_name, new_x, new_y, level_index=0):
        if level_index in self.levels:
            for token in self.levels[level_index]['tokens']:
                if token['name'] == token_name:
                    token['x'] = new_x
                    token['y'] = new_y
                    return True
        return False
        
    def get_token_at(self, x, y, level_index=0):
        if level_index not in self.levels: return None
        for token in reversed(self.levels[level_index]['tokens']):
            if math.sqrt((x - token['x'])**2 + (y - token['y'])**2) < 0.5:
                return token
        return None

    def get_all_tokens(self):
        all_tokens = []
        for level_data in self.levels.values():
            all_tokens.extend(level_data['tokens'])
        return all_tokens

    def calculate_distance(self, token1, token2):
        return math.sqrt((token1['x'] - token2['x'])**2 + (token1['y'] - token2['y'])**2)

    def save_map_data(self):
        json_path = os.path.join(self.maps_dir, f"{self.name.lower().replace(' ', '_')}.json")
        map_data = {
            'name': self.name, 'width': self.width, 'height': self.height, 
            'grid_size': self.grid_size, 'grid_scale': self.grid_scale,
            'map_type': self.map_type,
            'levels': self.levels,
        }
        with open(json_path, 'w') as f:
            json.dump(map_data, f, indent=4)

    @staticmethod
    def load(campaign_path, map_name):
        maps_dir = os.path.join(campaign_path, 'maps')
        json_path = os.path.join(maps_dir, f"{map_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(json_path): return None
        with open(json_path, 'r') as f:
            data = json.load(f)
            map_instance = MapModel(
                campaign_path, data['name'], data['width'], data['height'], 
                data.get('grid_size', 20), data.get('grid_scale', 1.5)
            )
            map_instance.map_type = data.get('map_type', 'outside')
            
            if 'map_elements' in data:
                 map_instance.levels = {0: {
                     'elements': data.get('map_elements', []), 
                     'tokens': data.get('tokens', []),
                     'landmarks': data.get('landmarks', []) # Legacy support
                }}
            else:
                 map_instance.levels = data.get('levels', {0: {'elements': [], 'tokens': [], 'landmarks': []}})
                 map_instance.levels = {int(k): v for k, v in map_instance.levels.items()}
                 # Ensure landmarks key exists for older saves
                 for level_data in map_instance.levels.values():
                     if 'landmarks' not in level_data:
                         level_data['landmarks'] = []
            return map_instance

    @staticmethod
    def get_all_maps(campaign_path):
        maps_dir = os.path.join(campaign_path, 'maps')
        if not os.path.exists(maps_dir): return []
        return sorted([f.replace('.json', '').replace('_', ' ').title() for f in os.listdir(maps_dir) if f.endswith('.json')])