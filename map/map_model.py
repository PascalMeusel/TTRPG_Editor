import json
import os
import random
import math
from PIL import Image, ImageDraw

class MapModel:
    """Manages all data for a map, including elements, tokens, and scale."""
    def __init__(self, name="New Map", width=80, height=60, grid_size=20, grid_scale=1.5):
        self.name = name
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.grid_scale = grid_scale # Meters per grid square
        self.map_elements = []
        self.tokens = []
        self.maps_dir = "data/maps"
        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)

    def clear_map(self):
        """Resets the map elements and tokens to a blank state."""
        self.map_elements = []
        self.tokens = []
        # Add a default background based on the model's dimensions
        self.add_element({'type': 'rect', 'coords': (0, 0, self.width, self.height), 'color': '#2B2B2B'})

    def add_element(self, element):
        self.map_elements.append(element)

    def add_token(self, name, token_type, x, y):
        if any(t['name'] == name for t in self.tokens):
            return False
        self.tokens.append({'name': name, 'type': token_type, 'x': x, 'y': y})
        return True

    def delete_token(self, token_name):
        """Removes a token from the map by its name."""
        self.tokens = [t for t in self.tokens if t.get('name') != token_name]

    def move_token(self, token_name, new_x, new_y):
        for token in self.tokens:
            if token['name'] == token_name:
                token['x'] = new_x
                token['y'] = new_y
                return True
        return False
        
    def get_token_at(self, x, y):
        """Finds the top-most token at a given grid coordinate."""
        for token in reversed(self.tokens):
            dist = math.sqrt((x - token['x'])**2 + (y - token['y'])**2)
            if dist < 0.5: # Click is within the token's grid cell
                return token
        return None

    def calculate_distance(self, token1, token2):
        """Calculates grid distance between the centers of two tokens."""
        dist = math.sqrt((token1['x'] - token2['x'])**2 + (token1['y'] - token2['y'])**2)
        return dist
        
    def generate_dungeon(self, room_max_size, room_min_size, max_rooms):
        """A simple dungeon generation algorithm."""
        self.clear_map()
        rooms = []
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

    def save_map(self):
        """Saves all map data to a JSON file and renders the background to a PNG."""
        json_path = os.path.join(self.maps_dir, f"{self.name.lower().replace(' ', '_')}.json")
        map_data = {
            'name': self.name, 'width': self.width, 'height': self.height, 
            'grid_size': self.grid_size, 'grid_scale': self.grid_scale,
            'elements': self.map_elements, 'tokens': self.tokens
        }
        with open(json_path, 'w') as f:
            json.dump(map_data, f, indent=4)
        self.render_background_to_png()

    def render_background_to_png(self):
        """Renders ONLY the map background elements to a PNG file."""
        png_path = os.path.join(self.maps_dir, f"{self.name.lower().replace(' ', '_')}.png")
        img_width, img_height = self.width * self.grid_size, self.height * self.grid_size
        image = Image.new('RGB', (img_width, img_height), '#000000')
        draw = ImageDraw.Draw(image)
        for elem in self.map_elements:
            coords = tuple(c * self.grid_size for c in elem['coords'])
            if elem['type'] == 'rect': draw.rectangle(coords, fill=elem['color'])
        image.save(png_path)

    @classmethod
    def load(cls, map_name, maps_dir="data/maps"):
        """Loads a map's data from a JSON file and returns a new MapModel instance."""
        json_path = os.path.join(maps_dir, f"{map_name.lower().replace(' ', '_')}.json")
        if not os.path.exists(json_path): return None
        with open(json_path, 'r') as f:
            data = json.load(f)
            map_instance = cls(
                data['name'], data['width'], data['height'], 
                data['grid_size'], data.get('grid_scale', 1.5) # Default to 1.5 for older maps
            )
            map_instance.map_elements = data.get('elements', [])
            map_instance.tokens = data.get('tokens', [])
            return map_instance

    @staticmethod
    def get_all_maps(maps_dir="data/maps"):
        """Returns a sorted list of all map names found in the data directory."""
        if not os.path.exists(maps_dir): return []
        return sorted([f.replace('.json', '').replace('_', ' ').title() for f in os.listdir(maps_dir) if f.endswith('.json')])