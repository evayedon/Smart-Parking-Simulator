# This module defines the Vehicle class, which represents a vehicle in a parking system.
#         """Get the current status of the parking spot"""

class Vehicle:
    def __init__(self, vehicle_id, vehicle_type, arrival_time, expected_duration):
        """
        Initialize a vehicle
        
        Args:
            vehicle_id (str): Unique identifier for the vehicle
            vehicle_type (str): Type of vehicle (compact, sedan, SUV, etc.)
            arrival_time (float): Time when the vehicle arrived
            expected_duration (float): Expected parking duration in minutes
        """
        self.id = vehicle_id
        self.type = vehicle_type
        self.arrival_time = arrival_time
        self.expected_duration = expected_duration
        self.assigned_spot = None
        self.preferences = {}
        
    def set_preferences(self, preferences):
        """
        Set parking preferences
        
        Args:
            preferences (dict): Dictionary of preferences like {"near_entrance": True}
        """
        self.preferences = preferences
        
    def assign_spot(self, spot_id):
        """Assign a parking spot to the vehicle"""
        self.assigned_spot = spot_id
        
    def __repr__(self):
        return f"Vehicle {self.id} ({self.type}) - Spot: {self.assigned_spot}"
