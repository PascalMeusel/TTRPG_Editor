import random

class MapGenerationModel:
    """A service model for generating different kinds of map data."""
    def __init__(self):
        pass

    def generate(self, gen_type, settings):
        """Public method to access different generators."""
        if gen_type == "Dungeon":
            return self.generate_dungeon(settings)
        else:
            return self.generate_blank_map(settings)

    def generate_blank_map(self, settings):
        width = settings.get('width', 50)
        height = settings.get('height', 50)
        map_data = {
            'width': width, # <-- ADDED
            'height': height, # <-- ADDED
            'grid_scale': settings.get('grid_scale', 1.5), # <-- ADDED
            'map_type': 'outside',
            'levels': {
                0: {
                    'elements': [{'type': 'rect', 'coords': (0, 0, width, height), 'color': '#2B2B2B'}],
                    'tokens': []
                }
            }
        }
        return map_data

    def generate_dungeon(self, settings):
        """Generates a multi-room dungeon. Returns map data dictionary."""
        width = settings.get('width', 50)
        height = settings.get('height', 50)
        room_max = settings.get('room_max_size', 12)
        room_min = settings.get('room_min_size', 5)
        max_rooms = settings.get('max_rooms', 30)
        
        elements = [{'type': 'rect', 'coords': (0, 0, width, height), 'color': '#2B2B2B'}]
        rooms = []
        
        for _ in range(max_rooms):
            w = random.randint(room_min, room_max)
            h = random.randint(room_min, room_max)
            x = random.randint(1, width - w - 2)
            y = random.randint(1, height - h - 2)
            new_room = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}

            if any(self._intersect(new_room, other) for other in rooms):
                continue

            elements.append({'type': 'rect', 'coords': (new_room['x1'], new_room['y1'], new_room['x2'], new_room['y2']), 'color': '#707070'})
            (new_x, new_y) = ((new_room['x1'] + new_room['x2']) // 2, (new_room['y1'] + new_room['y2']) // 2)

            if rooms:
                (prev_x, prev_y) = ((rooms[-1]['x1'] + rooms[-1]['x2']) // 2, (rooms[-1]['y1'] + rooms[-1]['y2']) // 2)
                if random.randint(0, 1) == 1:
                    self._create_h_corridor(elements, prev_x, new_x, prev_y)
                    self._create_v_corridor(elements, prev_y, new_y, new_x)
                else:
                    self._create_v_corridor(elements, prev_y, new_y, prev_x)
                    self._create_h_corridor(elements, prev_x, new_x, new_y)
            
            rooms.append(new_room)
        
        map_data = {
            'width': width, # <-- ADDED
            'height': height, # <-- ADDED
            'grid_scale': settings.get('grid_scale', 1.5), # <-- ADDED
            'map_type': 'inside',
            'levels': {0: {'elements': elements, 'tokens': []}}
        }
        return map_data

    def _intersect(self, room1, room2):
        return (room1['x1'] <= room2['x2'] and room1['x2'] >= room2['x1'] and
                room1['y1'] <= room2['y2'] and room1['y2'] >= room2['y1'])

    def _create_h_corridor(self, elements, x1, x2, y):
        elements.append({'type': 'rect', 'coords': (min(x1, x2), y, max(x1, x2) + 1, y + 1), 'color': '#707070'})

    def _create_v_corridor(self, elements, y1, y2, x):
        elements.append({'type': 'rect', 'coords': (x, min(y1, y2), x + 1, max(y1, y2) + 1), 'color': '#707070'})