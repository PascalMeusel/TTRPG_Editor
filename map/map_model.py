import json
import os
import random
from PIL import Image, ImageDraw

class MapModel:
    """
    Manages the data and logic for a single map, including drawing,
    procedural generation, and saving/loading.
    """
    def __init__(self, name="New Map", width=50, height=40, grid_size=20):
        self.name = name
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.map_elements = []
        self.maps_dir = "data/maps"
        if not os.path.exists(self.maps_dir):
            os.makedirs(self.maps_dir)

    def add_element(self, element):
        """Adds a drawn element (like a rect or line) to the map data."""
        self.map_elements.append(element)

    def generate_dungeon(self, room_max_size, room_min_size, max_rooms):
        """A simple dungeon generation algorithm."""
        self.map_elements = []
        rooms = []

        self.add_element({'type': 'rect', 'coords': (0, 0, self.width, self.height), 'color': '#3C3C3C'})

        for _ in range(max_rooms):
            w = random.randint(room_min_size, room_max_size)
            h = random.randint(room_min_size, room_max_size)
            x = random.randint(1, self.width - w - 2)
            y = random.randint(1, self.height - h - 2)
            
            new_room = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
            
            if any(self._intersect(new_room, other_room) for other_room in rooms):
                continue

            self.add_element({'type': 'rect', 'coords': (new_room['x1'], new_room['y1'], new_room['x2'], new_room['y2']), 'color': '#707070'})

            (new_x, new_y) = ((new_room['x1'] + new_room['x2']) // 2, (new_room['y1'] + new_room['y2']) // 2)

            if rooms:
                (prev_x, prev_y) = ((rooms[-1]['x1'] + rooms[-1]['x2']) // 2, (rooms[-1]['y1'] + rooms[-1]['y2']) // 2)
                
                # --- FIX: Ensure corridor coordinates are correctly ordered ---
                if random.randint(0, 1) == 1: # Horizontal then vertical
                    # Horizontal corridor
                    h_x0 = min(prev_x, new_x)
                    h_x1 = max(prev_x, new_x) + 1
                    self.add_element({'type': 'rect', 'coords': (h_x0, prev_y, h_x1, prev_y + 1), 'color': '#707070'})
                    # Vertical corridor
                    v_y0 = min(prev_y, new_y)
                    v_y1 = max(prev_y, new_y) + 1
                    self.add_element({'type': 'rect', 'coords': (new_x, v_y0, new_x + 1, v_y1), 'color': '#707070'})
                else: # Vertical then horizontal
                    # Vertical corridor
                    v_y0 = min(prev_y, new_y)
                    v_y1 = max(prev_y, new_y) + 1
                    self.add_element({'type': 'rect', 'coords': (prev_x, v_y0, prev_x + 1, v_y1), 'color': '#707070'})
                    # Horizontal corridor
                    h_x0 = min(prev_x, new_x)
                    h_x1 = max(prev_x, new_x) + 1
                    self.add_element({'type': 'rect', 'coords': (h_x0, new_y, h_x1, new_y + 1), 'color': '#707070'})
                # --- END FIX ---
            
            rooms.append(new_room)
        return True

    def _intersect(self, room1, room2):
        return (room1['x1'] <= room2['x2'] and room1['x2'] >= room2['x1'] and
                room1['y1'] <= room2['y2'] and room1['y2'] >= room2['y1'])

    def save_map(self, map_name):
        """Saves map data to JSON and renders a PNG image."""
        self.name = map_name
        json_path = os.path.join(self.maps_dir, f"{map_name.lower().replace(' ', '_')}.json")
        map_data = {
            'name': self.name, 'width': self.width, 'height': self.height, 
            'grid_size': self.grid_size, 'elements': self.map_elements
        }
        with open(json_path, 'w') as f:
            json.dump(map_data, f, indent=4)
        
        self.render_to_png(map_name)

    def render_to_png(self, map_name):
        """Renders the current map data to a PNG file."""
        png_path = os.path.join(self.maps_dir, f"{map_name.lower().replace(' ', '_')}.png")
        img_width = self.width * self.grid_size
        img_height = self.height * self.grid_size
        
        image = Image.new('RGB', (img_width, img_height), '#000000')
        draw = ImageDraw.Draw(image)

        for elem in self.map_elements:
            coords = tuple(c * self.grid_size for c in elem['coords'])
            if elem['type'] == 'rect':
                draw.rectangle(coords, fill=elem['color'])
            elif elem['type'] == 'line':
                 draw.line(coords, fill=elem['color'], width=elem.get('width', 1))

        image.save(png_path)

    @staticmethod
    def get_all_maps(maps_dir="data/maps"):
        """Returns a list of available map names."""
        if not os.path.exists(maps_dir): return []
        return sorted([f.replace('.png', '').replace('_', ' ').title() for f in os.listdir(maps_dir) if f.endswith('.png')])