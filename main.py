import tkinter as tk
from ParkingSimulatorGUI import ParkingSimulatorGUI

def main():
    """Main function to run the simulator"""
    root = tk.Tk()
    app = ParkingSimulatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()