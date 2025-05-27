import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from SmartParkingSimulator import SmartParkingSimulator


class ParkingSimulatorGUI:
    def __init__(self, root):
        """Initialize the GUI for the parking simulator"""
        self.root = root
        self.root.title("Smart Parking System Simulator")
        self.root.geometry("1200x800")
        
        self.simulator = SmartParkingSimulator()
        self.simulator.create_facility()
        
        self.create_widgets()
        self.update_interval = 100  # milliseconds
        self.is_simulation_running = False
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel for controls
        left_panel = ttk.LabelFrame(main_frame, text="Simulation Controls", padding="10")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Facility configuration
        facility_frame = ttk.LabelFrame(left_panel, text="Facility Configuration", padding="5")
        facility_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(facility_frame, text="Facility Layout:").pack(anchor=tk.W)
        self.layout_var = tk.StringVar(value="Default")
        layouts = ["Default", "Small", "Multi-Floor", "Large"]
        layout_menu = ttk.Combobox(facility_frame, textvariable=self.layout_var, values=layouts)
        layout_menu.pack(fill=tk.X, pady=3)
        layout_menu.bind("<<ComboboxSelected>>", self.on_layout_change)
        
        ttk.Label(facility_frame, text="Floor:").pack(anchor=tk.W)
        self.floor_var = tk.IntVar(value=0)
        floor_spinner = ttk.Spinbox(facility_frame, from_=0, to=3, textvariable=self.floor_var, width=5)
        floor_spinner.pack(fill=tk.X, pady=3)
        floor_spinner.bind("<<Increment>>", lambda e: self.update_visualization())
        floor_spinner.bind("<<Decrement>>", lambda e: self.update_visualization())
        
        # Simulation speed control
        ttk.Label(facility_frame, text="Simulation Speed:").pack(anchor=tk.W)
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(facility_frame, from_=0.1, to=10.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL)
        speed_scale.pack(fill=tk.X, pady=3)
        
        # Time settings
        time_frame = ttk.LabelFrame(left_panel, text="Time Settings", padding="5")
        time_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.time_label = ttk.Label(time_frame, text="Current Time: 12:00 AM")
        self.time_label.pack(anchor=tk.W, pady=3)
        
        day_frame = ttk.Frame(time_frame)
        day_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(day_frame, text="Day:").pack(side=tk.LEFT)
        self.day_var = tk.StringVar(value="Monday")
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_menu = ttk.Combobox(day_frame, textvariable=self.day_var, values=days, width=10)
        day_menu.pack(side=tk.LEFT, padx=5)
        day_menu.bind("<<ComboboxSelected>>", self.on_day_change)
        
        # Driver parameters
        driver_frame = ttk.LabelFrame(left_panel, text="Driver Parameters", padding="5")
        driver_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(driver_frame, text="Arrival Rate (vehicles/hour):").pack(anchor=tk.W)
        self.arrival_var = tk.DoubleVar(value=5.0)
        arrival_scale = ttk.Scale(driver_frame, from_=0.1, to=20.0, 
                                 variable=self.arrival_var, orient=tk.HORIZONTAL)
        arrival_scale.pack(fill=tk.X, pady=3)
        arrival_scale.bind("<ButtonRelease-1>", self.on_arrival_change)
        
        ttk.Label(driver_frame, text="Avg. Parking Duration (minutes):").pack(anchor=tk.W)
        self.duration_var = tk.DoubleVar(value=120.0)
        duration_scale = ttk.Scale(driver_frame, from_=15.0, to=480.0, 
                                  variable=self.duration_var, orient=tk.HORIZONTAL)
        duration_scale.pack(fill=tk.X, pady=3)
        duration_scale.bind("<ButtonRelease-1>", self.on_duration_change)
        
        # Vehicle type distribution
        vehicle_type_frame = ttk.Frame(driver_frame)
        vehicle_type_frame.pack(fill=tk.X, pady=3)
        
        ttk.Label(vehicle_type_frame, text="Vehicle Types:").pack(anchor=tk.W)
        
        # Standard vehicles
        std_frame = ttk.Frame(vehicle_type_frame)
        std_frame.pack(fill=tk.X, pady=2)
        ttk.Label(std_frame, text="Standard:").pack(side=tk.LEFT)
        self.std_var = tk.DoubleVar(value=80.0)
        ttk.Scale(std_frame, from_=0.0, to=100.0, variable=self.std_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(std_frame, textvariable=self.std_var).pack(side=tk.RIGHT, padx=5)
        
        # Handicap vehicles
        handicap_frame = ttk.Frame(vehicle_type_frame)
        handicap_frame.pack(fill=tk.X, pady=2)
        ttk.Label(handicap_frame, text="Handicap:").pack(side=tk.LEFT)
        self.handicap_var = tk.DoubleVar(value=10.0)
        ttk.Scale(handicap_frame, from_=0.0, to=100.0, variable=self.handicap_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(handicap_frame, textvariable=self.handicap_var).pack(side=tk.RIGHT, padx=5)
        
        # Electric vehicles
        electric_frame = ttk.Frame(vehicle_type_frame)
        electric_frame.pack(fill=tk.X, pady=2)
        ttk.Label(electric_frame, text="Electric:").pack(side=tk.LEFT)
        self.electric_var = tk.DoubleVar(value=10.0)
        ttk.Scale(electric_frame, from_=0.0, to=100.0, variable=self.electric_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(electric_frame, textvariable=self.electric_var).pack(side=tk.RIGHT, padx=5)
        
        # Driver preferences
        pref_frame = ttk.LabelFrame(driver_frame, text="Driver Preferences", padding="5")
        pref_frame.pack(fill=tk.X, pady=3)
        
        # Near entrance preference
        near_entrance_frame = ttk.Frame(pref_frame)
        near_entrance_frame.pack(fill=tk.X, pady=2)
        ttk.Label(near_entrance_frame, text="Near Entrance:").pack(side=tk.LEFT)
        self.near_entrance_var = tk.DoubleVar(value=60.0)
        ttk.Scale(near_entrance_frame, from_=0.0, to=100.0, variable=self.near_entrance_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(near_entrance_frame, textvariable=self.near_entrance_var).pack(side=tk.RIGHT, padx=5)
        
        # Easy exit preference
        easy_exit_frame = ttk.Frame(pref_frame)
        easy_exit_frame.pack(fill=tk.X, pady=2)
        ttk.Label(easy_exit_frame, text="Easy Exit:").pack(side=tk.LEFT)
        self.easy_exit_var = tk.DoubleVar(value=40.0)
        ttk.Scale(easy_exit_frame, from_=0.0, to=100.0, variable=self.easy_exit_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(easy_exit_frame, textvariable=self.easy_exit_var).pack(side=tk.RIGHT, padx=5)
        
        # Covered spot preference
        covered_spot_frame = ttk.Frame(pref_frame)
        covered_spot_frame.pack(fill=tk.X, pady=2)
        ttk.Label(covered_spot_frame, text="Covered Spot:").pack(side=tk.LEFT)
        self.covered_spot_var = tk.DoubleVar(value=30.0)
        ttk.Scale(covered_spot_frame, from_=0.0, to=100.0, variable=self.covered_spot_var, 
                 orient=tk.HORIZONTAL).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(covered_spot_frame, textvariable=self.covered_spot_var).pack(side=tk.RIGHT, padx=5)
        
        # Simulation control buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_simulation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button["state"] = "disabled"
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_simulation)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics", padding="5")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=30, wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        self.stats_text.configure(state="disabled")
        
        # Right panel for visualization
        right_panel = ttk.LabelFrame(main_frame, text="Facility Visualization", padding="10")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Matplotlib figure
        self.fig = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize visualization
        self.update_visualization()
        
    def start_simulation(self):
        """Start the simulation"""
        if not self.is_simulation_running:
            # Update parameters from UI
            self.update_simulation_parameters()
            
            # Start the simulator
            self.simulator.start_simulation()
            self.is_simulation_running = True
            
            # Update UI
            self.start_button["state"] = "disabled"
            self.stop_button["state"] = "normal"
            
            # Start update loop
            self.update_simulation()
            
    def stop_simulation(self):
        """Stop the simulation"""
        if self.is_simulation_running:
            self.simulator.stop_simulation()
            self.is_simulation_running = False
            
            # Update UI
            self.start_button["state"] = "normal"
            self.stop_button["state"] = "disabled"
            
    def reset_simulation(self):
        """Reset the simulation"""
        self.stop_simulation()
        
        # Recreate facility based on current layout
        layout = self.get_selected_layout()
        self.simulator = SmartParkingSimulator()
        self.simulator.create_facility(layout=layout)
        
        # Update visualization
        self.update_visualization()
        
        # Reset statistics display
        self.update_statistics()
        
    def update_simulation(self):
        """Update the simulation state and visualization"""
        if self.is_simulation_running:
            # Get simulation speed
            speed = self.speed_var.get()
            
            # Advance simulation
            time_step = 1.0 * speed  # minutes
            self.simulator.step_simulation(time_step)
            
            # Update visualization and statistics
            self.update_visualization()
            self.update_statistics()
            self.update_time_display()
            
            # Schedule next update
            self.root.after(self.update_interval, self.update_simulation)
            
    def update_visualization(self):
        """Update the visualization of the facility"""
        floor = self.floor_var.get()
        self.fig = self.simulator.visualize_facility(floor)
        
        # Update canvas
        self.canvas.figure = self.fig
        self.canvas.draw()
        
    def update_statistics(self):
        """Update statistics display"""
        if not self.simulator.facility:
            return
            
        stats = self.simulator.facility.get_occupancy_status()
        
        # Format statistics text
        stats_str = f"Total Spots: {stats['total_spots']}\n"
        stats_str += f"Occupied: {stats['occupied_spots']}\n"
        stats_str += f"Available: {stats['available_spots']}\n"
        stats_str += f"Occupancy Rate: {stats['occupancy_rate']*100:.1f}%\n\n"
        
        # Add vehicle type breakdown
        stats_str += "By Vehicle Type:\n"
        for spot_type, counts in stats["by_type"].items():
            if counts["total"] > 0:
                occ_rate = counts["occupied"] / counts["total"] * 100
                stats_str += f"{spot_type.title()}: {counts['occupied']}/{counts['total']} ({occ_rate:.1f}%)\n"
                
        # Add revenue information
        stats_str += f"\nTotal Revenue: ${stats['statistics']['revenue']:.2f}"
        
        # Update text widget
        self.stats_text.configure(state="normal")
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_str)
        self.stats_text.configure(state="disabled")
        
    def update_time_display(self):
        """Update the time display"""
        # Format time
        hour = int(self.simulator.time_of_day)
        minute = int((self.simulator.time_of_day - hour) * 60)
        am_pm = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
            
        # Get day name
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        day_name = days[self.simulator.day_of_week]
        
        time_str = f"Current Time: {display_hour}:{minute:02d} {am_pm}, {day_name}"
        self.time_label.config(text=time_str)
        
        # Update day dropdown without triggering event
        self.day_var.set(day_name)
        
    def update_simulation_parameters(self):
        """Update simulation parameters from UI values"""
        # Update arrival rate
        self.simulator.arrival_rate = self.arrival_var.get()
        
        # Update average parking duration
        self.simulator.avg_parking_duration = self.duration_var.get()
        
        # Update vehicle type distribution
        total = self.std_var.get() + self.handicap_var.get() + self.electric_var.get()
        if total > 0:
            self.simulator.vehicle_type_distribution = [
                self.std_var.get() / total,
                self.handicap_var.get() / total,
                self.electric_var.get() / total
            ]
            
        # Update driver preferences
        self.simulator.driver_preferences = {
            "near_entrance": self.near_entrance_var.get() / 100.0,
            "covered_spot": self.covered_spot_var.get() / 100.0,
            "easy_exit": self.easy_exit_var.get() / 100.0
        }
        
    def on_layout_change(self, event):
        """Handle layout selection change"""
        # Confirm with user before changing during running simulation
        if self.is_simulation_running:
            result = messagebox.askquestion("Change Layout", 
                                          "Changing layout will reset the simulation. Continue?",
                                          icon='warning')
            if result == 'no':
                # Reset combobox to current layout
                self.layout_var.set(self.simulator.facility.name)
                return
                
        # Reset simulation with new layout
        self.reset_simulation()
        
    def on_day_change(self, event):
        """Handle day selection change"""
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        selected_day = self.day_var.get()
        day_index = days.index(selected_day)
        
        # Update simulator day
        current_hour = self.simulator.time_of_day
        self.simulator.simulation_time = day_index * 24 * 60 + current_hour * 60
        self.simulator.day_of_week = day_index
        
        # Update display
        self.update_time_display()
        
    def on_arrival_change(self, event):
        """Handle arrival rate change"""
        if self.is_simulation_running:
            self.simulator.arrival_rate = self.arrival_var.get()
            
    def on_duration_change(self, event):
        """Handle parking duration change"""
        if self.is_simulation_running:
            self.simulator.avg_parking_duration = self.duration_var.get()
            
    def get_selected_layout(self):
        """Get the layout configuration based on selection"""
        selected = self.layout_var.get()
        
        if selected == "Small":
            return {
                "dimensions": (10, 8),
                "floors": 1,
                "spot_types": {
                    "standard": {"count": 40, "distribution": 0.8},
                    "handicap": {"count": 5, "distribution": 0.1},
                    "electric": {"count": 5, "distribution": 0.1}
                },
                "entrances": [(0, 4)],
                "exits": [(9, 4)],
                "aisles": [(x, 4) for x in range(10)]
            }
        elif selected == "Multi-Floor":
            return {
                "dimensions": (15, 12),
                "floors": 3,
                "spot_types": {
                    "standard": {"count": 300, "distribution": 0.8},
                    "handicap": {"count": 45, "distribution": 0.12},
                    "electric": {"count": 30, "distribution": 0.08}
                },
                "entrances": [(0, 6)],
                "exits": [(14, 6)],
                "aisles": [(x, y) for x in range(15) for y in [3, 6, 9]]
            }
        elif selected == "Large":
            return {
                "dimensions": (30, 20),
                "floors": 1,
                "spot_types": {
                    "standard": {"count": 400, "distribution": 0.75},
                    "handicap": {"count": 60, "distribution": 0.15},
                    "electric": {"count": 40, "distribution": 0.1}
                },
                "entrances": [(0, 5), (0, 15)],
                "exits": [(29, 5), (29, 15)],
                "aisles": [(x, y) for x in range(30) for y in [5, 10, 15]]
            }
        else:  # Default
            return None  # Use default layout from ParkingFacility

