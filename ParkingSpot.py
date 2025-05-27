import time


class ParkingSpot:
    def __init__(self, spot_id, location, spot_type, floor=0):
        """
        Initialize a parking spot
        
        Args:
            spot_id (str): Unique identifier for the spot
            location (tuple): (x, y) coordinates in the facility
            spot_type (str): Type of spot (standard, handicap, electric, etc.)
            floor (int): Floor level in multi-story facilities
        """
        self.id = spot_id
        self.location = location
        self.type = spot_type
        self.floor = floor
        self.occupied = False
        self.reserved = False
        self.vehicle_id = None
        self.occupied_since = None
        self.reserved_until = None
        
    def occupy(self, vehicle_id):
        """Occupy the spot with a vehicle"""
        if self.occupied or self.reserved:
            return False
        self.occupied = True
        self.vehicle_id = vehicle_id
        self.occupied_since = time.time()
        return True
        
    def vacate(self):
        """Vacate the spot"""
        if not self.occupied:
            return False
        self.occupied = False
        self.vehicle_id = None
        duration = time.time() - self.occupied_since
        self.occupied_since = None
        return duration
    
    def reserve(self, duration=30):
        """Reserve the spot for a duration (in minutes)"""
        if self.occupied or self.reserved:
            return False
        self.reserved = True
        self.reserved_until = time.time() + (duration * 60)
        return True
    
    def cancel_reservation(self):
        """Cancel a reservation"""
        if not self.reserved:
            return False
        self.reserved = False
        self.reserved_until = None
        return True
    
    def get_status(self):
        """Get the current status of the spot"""
        if self.occupied:
            return "occupied"
        elif self.reserved:
            return "reserved"
        else:
            return "available"
            
    def __repr__(self):
        return f"Spot {self.id} ({self.type}) - {self.get_status()}"