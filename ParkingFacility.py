import random
import heapq
from collections import defaultdict
from ParkingSpot import ParkingSpot



class ParkingFacility:
    def __init__(self, name, layout=None):
        """
        Initialize a parking facility
        
        Args:
            name (str): Name of the facility
            layout (dict): Dictionary defining the layout configuration
        """
        self.name = name
        self.spots = {}  # Hash map for O(1) lookup of spots
        self.vehicles = {}  # Hash map for vehicles currently in the facility
        self.occupancy_grid = {}  # Grid representation of occupancy
        self.layout = layout or self._default_layout()
        self.graph = {}  # Graph representation for pathfinding
        self.total_spots = 0
        self.available_spots = 0
        self.statistics = {
            "total_vehicles": 0,
            "avg_occupancy_rate": 0,
            "avg_search_time": 0,
            "revenue": 0
        }
        
        # Initialize the facility based on layout
        self._initialize_facility()
        
    def _default_layout(self):
        """Create a default layout if none provided"""
        return {
            "dimensions": (20, 15),  # (width, height)
            "floors": 1,
            "spot_types": {
                "standard": {"count": 150, "distribution": 0.8},
                "handicap": {"count": 20, "distribution": 0.1},
                "electric": {"count": 20, "distribution": 0.1}
            },
            "entrances": [(0, 7)], 
            "exits": [(19, 7)],
            "aisles": [(x, y) for x in range(20) for y in [3, 7, 11]]
        }
        
    def _initialize_facility(self):
        """Set up parking spots according to facility layout"""
        # Create a grid layout
        width, height = self.layout["dimensions"]
        floors = self.layout["floors"]
        
        # Initialize occupancy grid
        self.occupancy_grid = {
            floor: [[None for _ in range(width)] for _ in range(height)]
            for floor in range(floors)
        }
        
        # Create spots based on layout
        spot_id = 1
        for floor in range(floors):
            # Skip aisle positions and entrance/exit positions
            for y in range(height):
                for x in range(width):
                    # Skip aisles
                    if (x, y) in self.layout["aisles"] or \
                       (x, y) in self.layout["entrances"] or \
                       (x, y) in self.layout["exits"]:
                        continue
                    
                    # Determine spot type based on distribution
                    spot_type = self._determine_spot_type()
                    
                    # Create spot
                    spot = ParkingSpot(
                        f"{floor}-{spot_id}", 
                        (x, y), 
                        spot_type,
                        floor
                    )
                    
                    # Add to hash map and grid
                    self.spots[spot.id] = spot
                    self.occupancy_grid[floor][y][x] = spot.id
                    spot_id += 1
        
        # Update counts
        self.total_spots = len(self.spots)
        self.available_spots = self.total_spots
        
        # Build the navigation graph
        self._build_navigation_graph()
        
    def _determine_spot_type(self):
        """
        Determine spot type based on configured distribution
        Returns a spot type (e.g., 'standard', 'handicap', 'electric')
        """
        r = random.random()
        cumulative = 0
        for spot_type, info in self.layout["spot_types"].items():
            cumulative += info["distribution"]
            if r <= cumulative:
                return spot_type
        return "standard"  # Default fallback
        
    def _build_navigation_graph(self):
        """Build a graph representation for navigation/pathfinding"""
        width, height = self.layout["dimensions"]
        floors = self.layout["floors"]
        
        # Initialize graph
        self.graph = {}
        
        # Add nodes for all possible positions (including aisles)
        for floor in range(floors):
            for y in range(height):
                for x in range(width):
                    node_id = f"{floor}-{x}-{y}"
                    self.graph[node_id] = []
                    
                    # Add edges to adjacent nodes (4-way connectivity)
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            # Check if it's a valid move (e.g., not through walls)
                            self.graph[node_id].append(f"{floor}-{nx}-{ny}")
        
        # Add connections between floors (elevators/stairs)
        # For simplicity, we assume elevators at entrances connect floors
        for floor in range(floors - 1):
            for entrance in self.layout["entrances"]:
                x, y = entrance
                node_id1 = f"{floor}-{x}-{y}"
                node_id2 = f"{floor+1}-{x}-{y}"
                self.graph[node_id1].append(node_id2)
                self.graph[node_id2].append(node_id1)
                
    def find_nearest_available_spot(self, vehicle, location=None):
        """
        Find the nearest available parking spot using Dijkstra's algorithm
        
        Args:
            vehicle (Vehicle): Vehicle looking for parking
            location (tuple): Starting location, defaults to facility entrance
            
        Returns:
            str: ID of the nearest available spot, or None if none available
        """
        if self.available_spots == 0:
            return None
            
        # Default to first entrance if no location specified
        if location is None:
            floor = 0  # Default to ground floor
            x, y = self.layout["entrances"][0]
        else:
            floor, x, y = location
            
        start_node = f"{floor}-{x}-{y}"
        
        # Check for vehicle type compatibility with spots
        compatible_spots = []
        for spot_id, spot in self.spots.items():
            if not spot.occupied and not spot.reserved:
                # Apply vehicle preferences
                score = self._compute_spot_preference_score(spot, vehicle)
                compatible_spots.append((spot_id, score))
        
        if not compatible_spots:
            return None
            
        # Sort spots by preference score (higher is better)
        compatible_spots.sort(key=lambda x: x[1], reverse=True)
        
        # Take top 5 preferred spots and find the nearest one
        top_spots = compatible_spots[:5]
        
        # Find shortest path to each of the top spots
        best_spot = None
        shortest_distance = float('inf')
        
        for spot_id, _ in top_spots:
            spot = self.spots[spot_id]
            spot_node = f"{spot.floor}-{spot.location[0]}-{spot.location[1]}"
            
            # Find shortest path using Dijkstra's
            distance, _ = self._dijkstra(start_node, spot_node)
            
            if distance < shortest_distance:
                shortest_distance = distance
                best_spot = spot_id
                
        return best_spot
        
    def _compute_spot_preference_score(self, spot, vehicle):
        """
        Compute a preference score for a spot based on vehicle preferences
        Higher scores are better matches
        """
        score = 10.0  # Base score
        
        # Apply preferences if they exist
        if 'near_entrance' in vehicle.preferences and vehicle.preferences['near_entrance']:
            # Calculate distance to nearest entrance
            entrance_dist = min(
                self._manhattan_distance(spot.location, entrance)
                for entrance in self.layout["entrances"]
            )
            # Closer to entrance = higher score
            score += max(0, 5 - entrance_dist)
            
        # Prefer spots matching vehicle type
        if vehicle.type == "handicap" and spot.type == "handicap":
            score += 20
        elif vehicle.type == "electric" and spot.type == "electric":
            score += 15
        elif spot.type == "standard":
            score += 5
            
        return score
        
    def _manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
    def _dijkstra(self, start, target):
        """
        Implementation of Dijkstra's algorithm for shortest path
        
        Args:
            start (str): Starting node ID
            target (str): Target node ID
            
        Returns:
            tuple: (distance, path) where path is a list of nodes
        """
        # Initialize distances and priority queue
        distances = {node: float('inf') for node in self.graph}
        distances[start] = 0
        pq = [(0, start)]
        previous = {node: None for node in self.graph}
        
        while pq:
            current_distance, current_node = heapq.heappop(pq)
            
            # If we've reached the target
            if current_node == target:
                break
                
            # If we've found a worse path
            if current_distance > distances[current_node]:
                continue
                
            # Check all neighbors
            for neighbor in self.graph[current_node]:
                # Assume uniform edge weights of 1 for simplicity
                distance = current_distance + 1
                
                # If we've found a better path
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))
        
        # Reconstruct path
        path = []
        current = target
        while current:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        return distances[target], path
        
    def assign_vehicle_to_spot(self, vehicle, spot_id=None):
        """
        Assign a vehicle to a specific spot or find the best available spot
        
        Args:
            vehicle (Vehicle): Vehicle to assign
            spot_id (str): Specific spot ID, or None to find optimal spot
            
        Returns:
            bool: True if assignment successful, False otherwise
        """
        # If no specific spot requested, find optimal one
        if spot_id is None:
            spot_id = self.find_nearest_available_spot(vehicle)
            if spot_id is None:
                return False
                
        # Check if spot exists and is available
        if spot_id not in self.spots or self.spots[spot_id].occupied or self.spots[spot_id].reserved:
            return False
            
        # Assign spot
        spot = self.spots[spot_id]
        if spot.occupy(vehicle.id):
            vehicle.assign_spot(spot_id)
            self.vehicles[vehicle.id] = vehicle
            self.available_spots -= 1
            self.statistics["total_vehicles"] += 1
            return True
            
        return False
        
    def vacate_spot(self, spot_id):
        """
        Vacate a parking spot
        
        Args:
            spot_id (str): ID of the spot to vacate
            
        Returns:
            float: Duration of occupancy in minutes, or None if failed
        """
        if spot_id not in self.spots or not self.spots[spot_id].occupied:
            return None
            
        spot = self.spots[spot_id]
        vehicle_id = spot.vehicle_id
        
        # Calculate parking duration
        duration = spot.vacate()
        
        # Update vehicle and facility state
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]
            
        self.available_spots += 1
        
        # Update statistics - assume $2 per hour
        hours = duration / 3600
        self.statistics["revenue"] += hours * 2
        
        return duration / 60  # Convert to minutes
        
    def get_path_to_spot(self, start_location, spot_id):
        """
        Find path from a location to a specific spot
        
        Args:
            start_location (tuple): (floor, x, y) starting coordinates
            spot_id (str): Target spot ID
            
        Returns:
            list: Sequence of coordinates forming the path
        """
        floor, x, y = start_location
        start_node = f"{floor}-{x}-{y}"
        
        spot = self.spots[spot_id]
        target_node = f"{spot.floor}-{spot.location[0]}-{spot.location[1]}"
        
        _, path = self._dijkstra(start_node, target_node)
        
        # Convert path nodes to coordinates
        coordinates = []
        for node in path:
            parts = node.split('-')
            coordinates.append((int(parts[0]), int(parts[1]), int(parts[2])))
            
        return coordinates
        
    def get_occupancy_status(self):
        """Get current occupancy statistics"""
        occupied = self.total_spots - self.available_spots
        occupancy_rate = occupied / self.total_spots if self.total_spots > 0 else 0
        
        # Update rolling average
        self.statistics["avg_occupancy_rate"] = (
            self.statistics["avg_occupancy_rate"] * 0.95 + occupancy_rate * 0.05
        )
        
        status = {
            "total_spots": self.total_spots,
            "occupied_spots": occupied,
            "available_spots": self.available_spots,
            "occupancy_rate": occupancy_rate,
            "statistics": self.statistics
        }
        
        # Count by spot type
        status["by_type"] = defaultdict(lambda: {"total": 0, "occupied": 0})
        for spot in self.spots.values():
            status["by_type"][spot.type]["total"] += 1
            if spot.occupied:
                status["by_type"][spot.type]["occupied"] += 1
                
        return status

