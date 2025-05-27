import random
import heapq
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from Vehicle import Vehicle
from ParkingFacility import ParkingFacility


class SmartParkingSimulator:
    def __init__(self):
        """Initialize the smart parking simulator"""
        self.facility = None
        self.simulation_time = 0  # in minutes
        self.simulation_speed = 1  # multiplier
        self.vehicle_id_counter = 1
        self.events = []  # Priority queue for events
        self.vehicle_types = ["standard", "handicap", "electric"]
        self.vehicle_type_distribution = [0.8, 0.1, 0.1]  # Probabilities
        self.arrival_rate = 5  # vehicles per hour
        self.avg_parking_duration = 120  # minutes
        self.is_running = False
        self.time_of_day = 9  # 9 AM default
        self.day_of_week = 1  # Monday default (0=Sun, 6=Sat)
        
        # Default driver preferences - probability a driver has this preference
        self.driver_preferences = {
            "near_entrance": 0.6,
            "covered_spot": 0.3,
            "easy_exit": 0.4
        }
        
        # Set up visualization
        self.fig = None
        self.ax = None
        
    def create_facility(self, name=None, layout=None):
        """Create a new parking facility"""
        name = name or "Smart Parking Facility"
        self.facility = ParkingFacility(name, layout)
        
    def start_simulation(self):
        """Start the simulation"""
        if not self.facility:
            self.create_facility()
            
        self.is_running = True
        self.simulation_time = 0
        
        # Schedule initial vehicle arrivals
        self._schedule_next_arrival()
        
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        
    def step_simulation(self, time_step=1):
        """
        Advance simulation by time_step minutes
        
        Args:
            time_step (float): Minutes to advance
        """
        if not self.is_running:
            return
            
        target_time = self.simulation_time + time_step
        
        # Process all events until target_time
        while self.events and self.events[0][0] <= target_time:
            event_time, event_type, event_data = heapq.heappop(self.events)
            
            # Update simulation time to event time
            self.simulation_time = event_time
            
            # Process event
            if event_type == "arrival":
                self._process_vehicle_arrival(event_data)
            elif event_type == "departure":
                self._process_vehicle_departure(event_data)
                
        # Update simulation time to target time
        self.simulation_time = target_time
        
        # Update time of day
        real_minutes = self.simulation_time % (24 * 60)
        self.time_of_day = real_minutes / 60
        self.day_of_week = int(self.simulation_time / (24 * 60)) % 7
        
    def _schedule_next_arrival(self):
        """Schedule the next vehicle arrival based on arrival rate"""
        # Adjust arrival rate based on time of day and day of week
        adjusted_rate = self._adjust_arrival_rate()
        
        # Generate random time until next arrival (exponential distribution)
        if adjusted_rate > 0:
            mean_time_between_arrivals = 60 / adjusted_rate  # minutes
            time_until_next = random.expovariate(1 / mean_time_between_arrivals)
        else:
            time_until_next = float('inf')  # No arrivals if rate is 0
            
        # Schedule arrival event
        arrival_time = self.simulation_time + time_until_next
        vehicle = self._generate_random_vehicle(arrival_time)
        
        heapq.heappush(self.events, (arrival_time, "arrival", vehicle))
        
    def _adjust_arrival_rate(self):
        """
        Adjust arrival rate based on time of day and day of week
        Returns adjusted vehicles per hour
        """
        # Hour of day (0-23)
        hour = int(self.time_of_day)
        
        # Time of day factors (rush hours, etc.)
        time_factors = {
            6: 0.5, 7: 1.0, 8: 2.0, 9: 1.5,  # Morning rush
            12: 1.2, 13: 1.2,  # Lunch
            16: 1.5, 17: 2.0, 18: 1.8, 19: 1.0,  # Evening rush
        }
        time_factor = time_factors.get(hour, 0.5)
        
        # Weekend factor (weekends are less busy for work parking)
        weekend_factor = 0.6 if self.day_of_week in [0, 6] else 1.0
        
        # Compute adjusted rate
        adjusted_rate = self.arrival_rate * time_factor * weekend_factor
        
        return adjusted_rate
        
    def _generate_random_vehicle(self, arrival_time):
        """Generate a random vehicle based on configured distributions"""
        # Generate vehicle ID
        vehicle_id = f"V{self.vehicle_id_counter}"
        self.vehicle_id_counter += 1
        
        # Select vehicle type based on distribution
        vehicle_type = random.choices(self.vehicle_types, self.vehicle_type_distribution)[0]
        
        # Generate random parking duration (normal distribution around mean)
        duration = random.normalvariate(self.avg_parking_duration, self.avg_parking_duration / 4)
        duration = max(15, duration)  # Minimum 15 minutes
        
        # Create vehicle
        vehicle = Vehicle(vehicle_id, vehicle_type, arrival_time, duration)
        
        # Generate random preferences
        preferences = {}
        for pref, prob in self.driver_preferences.items():
            if random.random() < prob:
                preferences[pref] = True
                
        vehicle.set_preferences(preferences)
        
        return vehicle
        
    def _process_vehicle_arrival(self, vehicle):
        """Process a vehicle arrival event"""
        # Try to assign the vehicle to a spot
        if self.facility.assign_vehicle_to_spot(vehicle):
            # Schedule departure event
            departure_time = self.simulation_time + vehicle.expected_duration
            heapq.heappush(self.events, (departure_time, "departure", vehicle.assigned_spot))
        else:
            # Vehicle couldn't find a spot and leaves
            pass
            
        # Schedule next arrival
        self._schedule_next_arrival()
        
    def _process_vehicle_departure(self, spot_id):
        """Process a vehicle departure event"""
        # Vacate the spot
        self.facility.vacate_spot(spot_id)
        
    def visualize_facility(self, floor=0):
        """
        Visualize the current state of the parking facility
        
        Args:
            floor (int): Floor to visualize
        """
        if not self.facility:
            return
            
        width, height = self.facility.layout["dimensions"]
        
        if self.fig is None or self.ax is None:
            self.fig, self.ax = plt.subplots(figsize=(12, 8))
            
        # Clear previous visualization
        self.ax.clear()
        
        # Set up the grid
        self.ax.set_xlim(-1, width)
        self.ax.set_ylim(-1, height)
        self.ax.set_aspect('equal')
        self.ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        # Create a custom colormap for occupancy
        cmap = LinearSegmentedColormap.from_list('occupancy', 
                                               ['green', 'yellow', 'red'], 
                                               N=100)
        
        # Draw each parking spot
        for spot_id, spot in self.facility.spots.items():
            if spot.floor != floor:
                continue
                
            x, y = spot.location
            
            # Determine color based on status
            if spot.occupied:
                color = 'red'
            elif spot.reserved:
                color = 'yellow'
            else:
                color = 'green'
                
            # Different shape based on spot type
            if spot.type == 'handicap':
                marker = 's'  # square
                size = 120
            elif spot.type == 'electric':
                marker = 'D'  # diamond
                size = 100
            else:
                marker = 'o'  # circle
                size = 80
                
            self.ax.scatter(x, y, c=color, s=size, marker=marker, edgecolors='black')
            self.ax.text(x, y, spot_id.split('-')[1], ha='center', va='center', fontsize=8)
            
        # Mark entrances and exits
        for entrance in self.facility.layout["entrances"]:
            x, y = entrance
            self.ax.scatter(x, y, c='blue', s=150, marker='*', edgecolors='black')
            self.ax.text(x, y+0.3, "Entrance", ha='center', fontsize=10)
            
        for exit_pos in self.facility.layout["exits"]:
            x, y = exit_pos
            self.ax.scatter(x, y, c='purple', s=150, marker='X', edgecolors='black')
            self.ax.text(x, y+0.3, "Exit", ha='center', fontsize=10)
            
        # Add aisles and driving paths
        for aisle_pos in self.facility.layout["aisles"]:
            x, y = aisle_pos
            self.ax.add_patch(patches.Rectangle((x-0.5, y-0.5), 1, 1, 
                                              fill=True, color='lightgray', 
                                              alpha=0.3))
            
        # Add title and labels
        occupancy = self.facility.get_occupancy_status()
        title = f"{self.facility.name} - Floor {floor}\n"
        title += f"Time: {self._format_time()} - "
        title += f"Occupancy: {occupancy['occupied_spots']}/{occupancy['total_spots']} "
        title += f"({occupancy['occupancy_rate']*100:.1f}%)"
        
        self.ax.set_title(title)
        self.ax.set_xlabel("X Position")
        self.ax.set_ylabel("Y Position")
        
        # Add legend
        self.ax.scatter([], [], c='green', s=80, marker='o', edgecolors='black', label='Available')
        self.ax.scatter([], [], c='yellow', s=80, marker='o', edgecolors='black', label='Reserved')
        self.ax.scatter([], [], c='red', s=80, marker='o', edgecolors='black', label='Occupied')
        self.ax.scatter([], [], c='green', s=120, marker='s', edgecolors='black', label='Handicap')
        self.ax.scatter([], [], c='green', s=100, marker='D', edgecolors='black', label='Electric')
        self.ax.legend(loc='upper right')
        
        plt.tight_layout()
        return self.fig
        
    def _format_time(self):
        """Format the current simulation time as a time of day"""
        total_minutes = int(self.simulation_time % (24 * 60))
        hours = total_minutes // 60
        minutes = total_minutes % 60
        am_pm = "AM" if hours < 12 else "PM"
        display_hours = hours % 12
        if display_hours == 0:
            display_hours = 12
        return f"{display_hours}:{minutes:02d} {am_pm}"
