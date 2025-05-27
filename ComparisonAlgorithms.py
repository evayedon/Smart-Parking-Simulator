import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ComparisonAlgorithms:
    """Class to implement and compare different parking allocation algorithms"""
    
    @staticmethod
    def greedy_assignment(facility, vehicles):
        """
        Greedy algorithm: assigns each vehicle to the first available spot
        
        Args:
            facility (ParkingFacility): The parking facility
            vehicles (list): List of vehicles to assign
            
        Returns:
            dict: Mapping of vehicle IDs to assigned spot IDs
        """
        assignments = {}
        available_spots = [spot_id for spot_id, spot in facility.spots.items() 
                        if not spot.occupied and not spot.reserved]
        
        for vehicle in vehicles:
            if available_spots:
                spot_id = available_spots.pop(0)
                assignments[vehicle.id] = spot_id
                
        return assignments
        
    @staticmethod
    def nearest_spot_assignment(facility, vehicles, starting_pos=None):
        """
        Nearest spot algorithm: assigns each vehicle to the nearest available spot
        
        Args:
            facility (ParkingFacility): The parking facility
            vehicles (list): List of vehicles to assign
            starting_pos (tuple): Optional starting position (floor, x, y)
            
        Returns:
            dict: Mapping of vehicle IDs to assigned spot IDs
        """
        assignments = {}
        
        if starting_pos is None:
            # Default to first entrance
            floor = 0
            starting_pos = (floor,) + facility.layout["entrances"][0]
            
        for vehicle in vehicles:
            spot_id = facility.find_nearest_available_spot(vehicle, starting_pos)
            if spot_id:
                assignments[vehicle.id] = spot_id
                # Mark spot as unavailable for subsequent assignments
                facility.spots[spot_id].reserve()
                
        # Reset spots (unmark reservations made for algorithm)
        for spot_id in assignments.values():
            facility.spots[spot_id].cancel_reservation()
            
        return assignments
        
    @staticmethod
    def hungarian_assignment(facility, vehicles, starting_pos=None):
        """
        Hungarian algorithm: optimal assignment minimizing total cost
        
        Args:
            facility (ParkingFacility): The parking facility
            vehicles (list): List of vehicles to assign
            starting_pos (tuple): Optional starting position (floor, x, y)
            
        Returns:
            dict: Mapping of vehicle IDs to assigned spot IDs
        """
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        
        assignments = {}
        
        # Get available spots
        available_spots = [spot_id for spot_id, spot in facility.spots.items() 
                          if not spot.occupied and not spot.reserved]
        
        if not vehicles or not available_spots:
            return assignments
            
        # If more vehicles than spots, only assign up to available spots
        vehicles = vehicles[:len(available_spots)]
        
        # If more spots than vehicles, only consider a subset of spots
        if len(available_spots) > len(vehicles):
            # Filter to 2x the number of vehicles to reduce computation
            factor = min(2, len(available_spots) // len(vehicles))
            available_spots = available_spots[:len(vehicles) * factor]
            
        # Create cost matrix
        cost_matrix = np.zeros((len(vehicles), len(available_spots)))
        
        if starting_pos is None:
            # Default to first entrance
            floor = 0
            starting_pos = (floor,) + facility.layout["entrances"][0]
            
        # Fill cost matrix with distances from entrance to each spot
        for i, vehicle in enumerate(vehicles):
            for j, spot_id in enumerate(available_spots):
                spot = facility.spots[spot_id]
                
                # Base cost is distance
                spot_pos = (spot.floor,) + spot.location
                start_node = f"{starting_pos[0]}-{starting_pos[1]}-{starting_pos[2]}"
                end_node = f"{spot_pos[0]}-{spot_pos[1]}-{spot_pos[2]}"
                
                try:
                    distance, _ = facility._dijkstra(start_node, end_node)
                except:
                    # Fallback if pathfinding fails
                    distance = abs(starting_pos[1] - spot_pos[1]) + abs(starting_pos[2] - spot_pos[2])
                
                # Adjust cost based on vehicle preferences
                preference_score = facility._compute_spot_preference_score(spot, vehicle)
                
                # Final cost is distance minus preference score (for minimization)
                cost = distance - (preference_score / 5)
                cost_matrix[i, j] = max(0.1, cost)  # Ensure positive cost
                
        # Solve assignment problem
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        
        # Create assignments
        for i, j in zip(row_ind, col_ind):
            vehicle = vehicles[i]
            spot_id = available_spots[j]
            assignments[vehicle.id] = spot_id
            
        return assignments
        
    @staticmethod
    def compare_algorithms(facility, vehicles, algorithms=None):
        """
        Compare different assignment algorithms
        
        Args:
            facility (ParkingFacility): The parking facility
            vehicles (list): List of vehicles to assign
            algorithms (list): List of algorithm functions to compare
            
        Returns:
            dict: Results of algorithm comparison
        """
        if algorithms is None:
            algorithms = [
                ("Greedy", ComparisonAlgorithms.greedy_assignment),
                ("Nearest Spot", ComparisonAlgorithms.nearest_spot_assignment),
                ("Hungarian (Optimal)", ComparisonAlgorithms.hungarian_assignment)
            ]
            
        results = {}
        
        # Deep copy of facility and vehicles to avoid contamination
        import copy
        
        for name, algorithm in algorithms:
            # Clone facility and vehicles
            facility_copy = copy.deepcopy(facility)
            vehicles_copy = copy.deepcopy(vehicles)
            
            # Measure assignment time
            start_time = time.time()
            assignments = algorithm(facility_copy, vehicles_copy)
            end_time = time.time()
            
            # Compute metrics
            total_distance = 0
            preference_satisfaction = 0
            
            # Default starting position (entrance)
            floor = 0
            starting_pos = (floor,) + facility.layout["entrances"][0]
            
            for vehicle_id, spot_id in assignments.items():
                vehicle = next(v for v in vehicles_copy if v.id == vehicle_id)
                spot = facility_copy.spots[spot_id]
                
                # Calculate distance
                spot_pos = (spot.floor,) + spot.location
                start_node = f"{starting_pos[0]}-{starting_pos[1]}-{starting_pos[2]}"
                end_node = f"{spot_pos[0]}-{spot_pos[1]}-{spot_pos[2]}"
                
                try:
                    distance, _ = facility_copy._dijkstra(start_node, end_node)
                except:
                    # Fallback if pathfinding fails
                    distance = abs(starting_pos[1] - spot_pos[1]) + abs(starting_pos[2] - spot_pos[2])
                
                total_distance += distance
                
                # Calculate preference satisfaction
                preference_score = facility_copy._compute_spot_preference_score(spot, vehicle)
                preference_satisfaction += preference_score
                
            # Store results
            results[name] = {
                "assignments": len(assignments),
                "avg_distance": total_distance / len(assignments) if assignments else 0,
                "avg_preference": preference_satisfaction / len(assignments) if assignments else 0,
                "execution_time": end_time - start_time
            }
            
        return results
