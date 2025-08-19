import random
import heapq

class MapGenerationModel:
    # ... (generate, _get_base_map_data, generate_blank_map are unchanged) ...
    def generate(self, gen_type, settings):
        if gen_type == "Dungeon":
            return self.generate_dungeon(settings)
        elif gen_type == "Winding Road":
            return self.generate_winding_road(settings)
        elif gen_type == "Simple Town":
            layout = settings.get("town_layout", "Crossroads")
            if layout == "Main Street":
                return self._generate_main_street_town(settings)
            elif layout == "Riverside":
                return self._generate_riverside_town(settings)
            else:
                return self._generate_crossroads_town(settings)
        else:
            return self.generate_blank_map(settings)
    def _get_base_map_data(self, settings, map_type='outside', bg_color='#6B8E23'):
        width = settings.get('width', 50)
        height = settings.get('height', 50)
        return {
            'width': width, 'height': height, 'grid_scale': settings.get('grid_scale', 1.5),
            'map_type': map_type,
            'levels': { 0: { 'elements': [{'type': 'rect', 'coords': (0, 0, width, height), 'color': bg_color}], 'tokens': [], 'landmarks': [] } }
        }
    def generate_blank_map(self, settings):
        return self._get_base_map_data(settings, bg_color='#2B2B2B')

    def generate_dungeon(self, settings):
        map_data = self._get_base_map_data(settings, map_type='inside', bg_color='#2B2B2B')
        elements, landmarks = map_data['levels'][0]['elements'], map_data['levels'][0]['landmarks']
        width, height = map_data['width'], map_data['height']
        
        num_rooms = settings.get("dungeon_rooms", 30)
        min_size = settings.get("dungeon_min_size", 5)
        max_size = settings.get("dungeon_max_size", 12)

        rooms = []
        for _ in range(num_rooms * 3):
            if len(rooms) >= num_rooms: break
            w, h = random.randint(min_size, max_size), random.randint(min_size, max_size)
            x, y = random.randint(1, width - w - 2), random.randint(1, height - h - 2)
            new_room = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
            if any(self._intersect(new_room, other, padding=2) for other in rooms): continue
            
            elements.append({'type': 'rect', 'coords': (new_room['x1'], new_room['y1'], new_room['x2'], new_room['y2']), 'color': '#707070'})
            if rooms:
                prev_center = ((rooms[-1]['x1'] + rooms[-1]['x2']) // 2, (rooms[-1]['y1'] + rooms[-1]['y2']) // 2)
                new_center = ((new_room['x1'] + new_room['x2']) // 2, (new_room['y1'] + new_room['y2']) // 2)
                # --- FIX: Pass the list of rooms as obstacles ---
                self._create_corridor(elements, prev_center, new_center, obstacles=rooms)
            rooms.append(new_room)
            
        if rooms:
            landmarks.append({'x': (rooms[0]['x1']+rooms[0]['x2'])//2, 'y': (rooms[0]['y1']+rooms[0]['y2'])//2, 'text': 'Entrance'})
            if len(rooms) > 1:
                landmarks.append({'x': (rooms[-1]['x1']+rooms[-1]['x2'])//2, 'y': (rooms[-1]['y1']+rooms[-1]['y2'])//2, 'text': 'Treasure'})
        return map_data

    def generate_winding_road(self, settings):
        map_data = self._get_base_map_data(settings, bg_color='#228B22')
        elements, landmarks = map_data['levels'][0]['elements'], map_data['levels'][0]['landmarks']
        width, height = map_data['width'], map_data['height']
        
        path_width = settings.get("road_path_width", 3)
        scenery_density = settings.get("road_scenery_density", 70)

        y = height // 2
        path_elements = []
        for x in range(width):
            path_rect = {'type': 'rect', 'coords': (x, y - path_width//2, x + 1, y + path_width//2 + 1), 'color': '#D2B48C'}
            elements.append(path_rect)
            path_elements.append(path_rect)
            y += random.randint(-1, 1)
            y = max(path_width, min(y, height - path_width))
        for _ in range(scenery_density):
            px, py = random.randint(0, width-1), random.randint(0, height-1)
            point_rect = {'x1':px, 'y1':py, 'x2':px+1, 'y2':py+1}
            if not any(self._intersect(point_rect, path_elem) for path_elem in path_elements):
                elements.append({'type': 'rect', 'coords': (px, py, px+1, py+1), 'color': '#696969'})
        landmarks.append({'x': 1, 'y': height//2, 'text': 'Start'})
        landmarks.append({'x': width-2, 'y': y, 'text': 'End'})
        landmarks.append({'x': width//2, 'y': height - 5, 'text': 'Cave'})
        return map_data

    def _generate_crossroads_town(self, settings):
        map_data = self._get_base_map_data(settings, bg_color='#6B8E23')
        elements, landmarks = map_data['levels'][0]['elements'], map_data['levels'][0]['landmarks']
        width, height = map_data['width'], map_data['height']
        road_color, path_color, bld_color = '#D2B48C', '#BC8F8F', '#8B4513'
        num_buildings = settings.get("town_buildings", 15)
        h_road_y, v_road_x = height // 2, width // 2
        road_w, square_s = 2, random.randint(4, 6)
        no_build_zones = []
        roads = [
            {'x1': 0, 'y1': h_road_y - road_w//2, 'x2': v_road_x - square_s, 'y2': h_road_y + road_w//2},
            {'x1': v_road_x + square_s, 'y1': h_road_y - road_w//2, 'x2': width, 'y2': h_road_y + road_w//2},
            {'x1': v_road_x - road_w//2, 'y1': 0, 'x2': v_road_x + road_w//2, 'y2': h_road_y - square_s},
            {'x1': v_road_x - road_w//2, 'y1': h_road_y + square_s, 'x2': v_road_x + road_w//2, 'y2': height},
            {'x1': v_road_x - square_s, 'y1': h_road_y - square_s, 'x2': v_road_x + square_s, 'y2': h_road_y + square_s}
        ]
        no_build_zones.extend(roads)
        for road in roads: elements.append({'type': 'rect', 'coords': (road['x1'], road['y1'], road['x2'], road['y2']), 'color': road_color})
        buildings = self._place_buildings(width, height, no_build_zones, num_buildings, num_buildings)
        for b in buildings:
            elements.append({'type': 'rect', 'coords': (b['x1'], b['y1'], b['x2'], b['y2']), 'color': bld_color})
            door_pos = self._find_door_location(b, v_road_x, h_road_y)
            self._create_path_to_road(elements, door_pos, v_road_x, h_road_y, path_color, buildings)
        landmarks.extend([{'x': v_road_x, 'y': h_road_y, 'text': 'Town Square'}, {'x': v_road_x + 2, 'y': h_road_y + 2, 'text': 'Fountain'}])
        return map_data

    def _generate_main_street_town(self, settings):
        map_data = self._get_base_map_data(settings, bg_color='#6B8E23')
        elements, landmarks = map_data['levels'][0]['elements'], map_data['levels'][0]['landmarks']
        width, height = map_data['width'], map_data['height']
        road_color, path_color, bld_color = '#D2B48C', '#BC8F8F', '#8B4513'
        num_buildings = settings.get("town_buildings", 15)
        road_pos, road_w = width // 2, 3
        road = {'x1': road_pos - road_w//2, 'y1': 0, 'x2': road_pos + road_w//2 + 1, 'y2': height}
        no_build_zones = [road]
        elements.append({'type': 'rect', 'coords': (road['x1'], road['y1'], road['x2'], road['y2']), 'color': road_color})
        buildings = self._place_buildings(width, height, no_build_zones, num_buildings, num_buildings)
        for b in buildings:
            elements.append({'type': 'rect', 'coords': (b['x1'], b['y1'], b['x2'], b['y2']), 'color': bld_color})
            door_pos = self._find_door_location(b, road_pos, None)
            self._create_path_to_road(elements, door_pos, road_pos, None, path_color, buildings)
        landmarks.extend([{'x': road_pos, 'y': 5, 'text': 'North Gate'}, {'x': road_pos, 'y': height - 5, 'text': 'South Gate'}])
        return map_data

    def _generate_riverside_town(self, settings):
        map_data = self._get_base_map_data(settings, bg_color='#6B8E23')
        elements, landmarks = map_data['levels'][0]['elements'], map_data['levels'][0]['landmarks']
        width, height = map_data['width'], map_data['height']
        river_color, path_color, bld_color, wood_color = '#4682B4', '#BC8F8F', '#8B4513', '#A0522D'
        num_buildings = settings.get("town_buildings", 10)
        no_build_zones = []
        river_x, river_w = width // 3, 5
        y = 0
        while y < height:
            river_segment = {'x1': river_x - river_w, 'y1': y, 'x2': river_x + river_w, 'y2': y + 1}
            elements.append({'type': 'rect', 'coords': (river_segment['x1'], river_segment['y1'], river_segment['x2'], river_segment['y2']), 'color': river_color})
            no_build_zones.append(river_segment)
            river_x += random.randint(-1, 1)
            river_x = max(river_w + 1, min(river_x, width - river_w - 1))
            y += 1
        bridge_y = height // 2
        bridge = {'x1': 0, 'y1': bridge_y, 'x2': width, 'y2': bridge_y + 2}
        no_build_zones.append(bridge)
        elements.append({'type': 'rect', 'coords': (bridge['x1'], bridge['y1'], bridge['x2'], bridge['y2']), 'color': wood_color})
        landmarks.append({'x': river_x, 'y': bridge_y, 'text': 'Bridge'})
        buildings = self._place_buildings(width, height, no_build_zones, num_buildings, num_buildings, safe_zone_x_min=river_x + river_w)
        for b in buildings:
            elements.append({'type': 'rect', 'coords': (b['x1'], b['y1'], b['x2'], b['y2']), 'color': bld_color})
            door_pos = self._find_door_location(b, None, bridge_y)
            self._create_path_to_road(elements, door_pos, None, bridge_y, path_color, buildings)
        landmarks.append({'x': river_x + 8, 'y': bridge_y + 8, 'text': 'Ferry Dock'})
        return map_data

    def _place_buildings(self, width, height, no_build_zones, min_bld, max_bld, safe_zone_x_min=1):
        buildings = []
        for _ in range(random.randint(min_bld, max_bld)):
            w, h = random.randint(4, 9), random.randint(4, 9)
            for _ in range(50):
                x = random.randint(safe_zone_x_min, width - w - 1)
                y = random.randint(1, height - h - 1)
                new_b = {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h}
                if not any(self._intersect(new_b, b, padding=2) for b in buildings) and \
                   not any(self._intersect(new_b, z) for z in no_build_zones):
                    buildings.append(new_b)
                    break
        return buildings

    def _find_door_location(self, building, v_road_x, h_road_y):
        dist_v, dist_h = float('inf'), float('inf')
        if v_road_x is not None:
            dist_v = min(abs(building['x1'] - v_road_x), abs(building['x2'] - v_road_x))
        if h_road_y is not None:
            dist_h = min(abs(building['y1'] - h_road_y), abs(building['y2'] - h_road_y))
        door_y = random.randint(building['y1'] + 1, building['y2'] - 2)
        door_x = random.randint(building['x1'] + 1, building['x2'] - 2)
        if dist_v < dist_h:
            if abs(building['x1'] - v_road_x) < abs(building['x2'] - v_road_x): return (building['x1'], door_y)
            else: return (building['x2'], door_y)
        else:
            if abs(building['y1'] - h_road_y) < abs(building['y2'] - h_road_y): return (door_x, building['y1'])
            else: return (door_x, building['y2'])

    def _create_path_to_road(self, elements, door_pos, v_road_x, h_road_y, color, obstacles):
        x1, y1 = door_pos
        if v_road_x is not None and (h_road_y is None or abs(x1 - v_road_x) < abs(y1 - h_road_y)):
            x2, y2 = v_road_x, y1
        elif h_road_y is not None:
            x2, y2 = x1, h_road_y
        else: return
        path = self._astar_pathfind((x1, y1), (x2, y2), obstacles)
        if path:
            for point in path:
                elements.append({'type': 'rect', 'coords': (point[0], point[1], point[0] + 1, point[1] + 1), 'color': color})

    def _intersect(self, r1, r2, padding=0):
        r2_x1, r2_y1, r2_x2, r2_y2 = r2.get('x1'), r2.get('y1'), r2.get('x2'), r2.get('y2')
        if 'coords' in r2:
            r2_x1, r2_y1, r2_x2, r2_y2 = r2['coords']
        return (r1['x1'] < r2_x2 + padding and r1['x2'] + padding > r2_x1 and
                r1['y1'] < r2_y2 + padding and r1['y2'] + padding > r2_y1)

    def _create_corridor(self, elements, p1, p2, obstacles=[], color='#707070', width=1):
        path = self._astar_pathfind(p1, p2, obstacles)
        if path:
            for point in path:
                elements.append({'type': 'rect', 'coords': (point[0], point[1], point[0] + width, point[1] + width), 'color': color})

    def _astar_pathfind(self, start, end, obstacles):
        open_set_heap = []
        heapq.heappush(open_set_heap, (0, start))
        open_set_hash = {start}
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0] - end[0]) + abs(start[1] - end[1])}
        obstacle_map = set()
        for obs in obstacles:
            for x in range(obs['x1'], obs['x2']):
                for y in range(obs['y1'], obs['y2']):
                    obstacle_map.add((x, y))
        while open_set_heap:
            _, current = heapq.heappop(open_set_heap)
            open_set_hash.remove(current)
            if current == end:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (current[0] + dx, current[1] + dy)
                if neighbor in obstacle_map:
                    continue
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + abs(neighbor[0] - end[0]) + abs(neighbor[1] - end[1])
                    if neighbor not in open_set_hash:
                        heapq.heappush(open_set_heap, (f_score[neighbor], neighbor))
                        open_set_hash.add(neighbor)
        return None