import json
import os
import random
import math

class MapModel:
    """Manages map data, focusing on metadata and tokens. The visual background is handled as an image."""
    def __init__(self, name="New Map", width=80, height=60, grid_size=20, grid_scale=1.5):
        self.name = name
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_scale = grid_scale
        self.map_elements = [] # This is now transient data for the editor session
        self.tokens = []
        self.maps_dir = "data/maps"
        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)

    def clear_map(self):
        """Resets the map elements and tokens to a blank state."""
        self.map_elements = []
        self.tokens = []
        self.add_element({'type': 'rect', 'coords': (0, 0, self.width, self.height), 'color': '#2B2B2B'})

    def add_element(self, element):
        self.map_elements.append(element)

    def add_token(self, name, token_type, x, y):
        if any(t['name'] == name for t in self.tokens): return False
        self.tokens.append({'name': name, 'type': token_type, 'x': x, 'y': y})
        return True

    def delete_token(self, token_name):
        self.tokens = [t for t in self.tokens if t.get('name') != token_name]

    def move_token(self, token_name, new_x, new_y):
        for token in self.tokens:
            if token['name'] == token_name:
                token['x'] = new_x
                token['y'] = new_y
                return True
        return False
        
    def get_token_at(self, x, y):
        for token in reversed(self.tokens):
            if math.sqrt((x - token['x'])**2 + (y - token['y'])**2) < 0.5:
                return token
        return None

    def calculate_distance(self, token1, token2):
        return math.sqrt((token1['x'] - token2['x'])**2 + (token1['y'] - token2['y'])**2)
        
    def generate_dungeon(self, room_max_size, room_min_size, max_rooms):
        self.clear_map()
        rooms = []
        # ... (generation logic remains the same) ...
        for _ in range(max_rooms):
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            new_room = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
            if any(self._intersect(new_room, other_room) for other_room in rooms): continue
            self.add_element({'type': 'rect', 'coords': (new_room['x1'], new_room['y1'], new_room['x2'], new_room['y2']), 'color': '#707070'})
            (new_x, new_y) = ((new_room['x1'] + new_room['x2']) // 2, (new_room['y1'] + new_room['y2']) // 2)
            if rooms:
                (prev_x, prev_y) = ((rooms[-1]['x1'] + rooms[-1]['x2']) // 2, (rooms[-1]['y1'] + rooms[-1]['y2']) // 2)
                if random.randint(0, 1) == 1:
                    self.add_element({'type': 'rect', 'coords': (min(prev_x, new_x), prev_y, max(prev_x, new_x) + 1, prev_y + 1), 'color': '#707070'})
                    self.add_element({'type': 'rect', 'coords': (new_x, min(prev_y, new_y), new_x + 1, max(prev_y, new_y) + 1), 'color': '#707070'})
                else:
                    self.add_element({'type': 'rect', 'coords': (prev_x, min(prev_y, new_y), prev_x + 1, max(prev_y, new_y) + 1), 'color': '#707070'})
                    self.add_element({'type': 'rect', 'coords': (min(prev_x, new_x), new_y, max(prev_x, new_x) + 1, new_y + 1), 'color': '#707070'})
            rooms.append(new_room)
        return True

    def _intersect(self, room1, room2):
        return (room1['x1'] <= room2['x2'] and room1['x2'] >= room2['x1'] and
                room1['y1'] <= room2['y2'] and room1['y2'] >= room2['y1'])

    def save_map_data(self):
        """Saves only metadata and tokens to a lightweight JSON file."""
        json_path = os.path.join(self.maps_dir, f"{self.name.lower().replace(' ', '_')}.json")
        map_data = {
            'name': self.name, 'width': self.width, 'height': self.height, 
            'grid_size': self.grid_size, 'grid_scale': self.grid_scale,
            'tokens': self.tokens
            # 'elements' list is NOT saved anymore
        }
        with open(json_path, 'w') as f:
            json.dump(map_data, f, indent=4)

    @classmethod
    def load(cls, map_name, maps_dir="data/maps"):
        """Loads metadata and tokens from a JSON file."""
        json_path = os.path.join(maps_dir, f"{map_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(json_path): return None
        with open(json_path, 'r') as f:
            data = json.load(f)
            map_instance = cls(
                data['name'], data['width'], data['height'], 
                data['grid_size'], data.get('grid_scale', 1.5)
            )
            # The loaded instance will have an empty map_elements list, which is correct.
            # The visual background will be loaded from the PNG in the view.
            map_instance.tokens = data.get('tokens', [])
            return map_instance

    @staticmethod
    def get_all_maps(maps_dir="data/maps"):
        return sorted([f.replace('.json', '').replace('_', ' ').title() for f in os.listdir(maps_dir) if f.endswith('.json')])