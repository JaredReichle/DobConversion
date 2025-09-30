#!/usr/bin/env python3
"""
Stellarium Mount Interface
Python script to interface between Stellarium and Arduino mount controller

This script can:
1. Read telescope coordinates from Stellarium
2. Convert coordinates to motor steps
3. Send commands to Arduino
4. Monitor mount status

Requirements:
- pyserial
- socket (for Stellarium communication)
"""

import serial
import socket
import time
import math
import threading
from typing import Tuple, Optional
import struct

class StellariumMountInterface:
    def __init__(self, arduino_port: str = 'COM3', baud_rate: int = 9600):
        """
        Initialize the mount interface
        
        Args:
            arduino_port: Serial port for Arduino (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baud_rate: Serial communication baud rate
        """
        self.arduino_port = arduino_port
        self.baud_rate = baud_rate
        self.serial_conn = None
        self.connected = False
        
        # Motor parameters (matching Arduino code)
        self.STEPS_PER_REVOLUTION = 2048
        self.AZIMUTH_MAX_STEPS = self.STEPS_PER_REVOLUTION
        self.ALTITUDE_MAX_STEPS = self.STEPS_PER_REVOLUTION // 2
        
        # Current position tracking
        self.current_azimuth_steps = 0
        self.current_altitude_steps = 0
        self.azimuth_moving = False
        self.altitude_moving = False
        
        # Stellarium connection
        self.stellarium_socket = None
        self.stellarium_connected = False
        
    def connect_arduino(self) -> bool:
        """Connect to Arduino via serial"""
        try:
            self.serial_conn = serial.Serial(self.arduino_port, self.baud_rate, timeout=1)
            time.sleep(2)  # Wait for Arduino to reset
            self.connected = True
            print(f"Connected to Arduino on {self.arduino_port}")
            
            # Clear any pending data
            self.serial_conn.reset_input_buffer()
            
            # Get initial status
            self.get_status()
            return True
            
        except serial.SerialException as e:
            print(f"Failed to connect to Arduino: {e}")
            self.connected = False
            return False
    
    def disconnect_arduino(self):
        """Disconnect from Arduino"""
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        self.connected = False
        print("Disconnected from Arduino")
    
    def send_command(self, command: str) -> str:
        """Send command to Arduino and return response"""
        if not self.connected:
            return "ERROR: Not connected to Arduino"
        
        try:
            # Send command
            self.serial_conn.write(f"{command}\n".encode())
            
            # Read response
            response = ""
            timeout = time.time() + 2  # 2 second timeout
            
            while time.time() < timeout:
                if self.serial_conn.in_waiting:
                    line = self.serial_conn.readline().decode().strip()
                    if line:
                        response += line + "\n"
                        if "ERROR" in line or "Target reached" in line:
                            break
                time.sleep(0.01)
            
            return response.strip()
            
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            return f"ERROR: {e}"
    
    def get_status(self) -> dict:
        """Get current mount status"""
        response = self.send_command("STATUS")
        
        # Parse status response
        # Expected format: "STATUS: AZ=100, AL=50, AZ_MOVING=0, AL_MOVING=0"
        try:
            if "STATUS:" in response:
                parts = response.split("STATUS:")[1].strip().split(",")
                for part in parts:
                    if "AZ=" in part:
                        self.current_azimuth_steps = int(part.split("=")[1])
                    elif "AL=" in part:
                        self.current_altitude_steps = int(part.split("=")[1])
                    elif "AZ_MOVING=" in part:
                        self.azimuth_moving = part.split("=")[1] == "1"
                    elif "AL_MOVING=" in part:
                        self.altitude_moving = part.split("=")[1] == "1"
        except:
            pass
        
        return {
            'azimuth_steps': self.current_azimuth_steps,
            'altitude_steps': self.current_altitude_steps,
            'azimuth_moving': self.azimuth_moving,
            'altitude_moving': self.altitude_moving,
            'azimuth_degrees': self.steps_to_degrees(self.current_azimuth_steps, True),
            'altitude_degrees': self.steps_to_degrees(self.current_altitude_steps, False)
        }
    
    def move_azimuth(self, steps: int) -> str:
        """Move azimuth motor to specified step position"""
        return self.send_command(f"AZ,{steps}")
    
    def move_altitude(self, steps: int) -> str:
        """Move altitude motor to specified step position"""
        return self.send_command(f"AL,{steps}")
    
    def move_to_coordinates(self, azimuth_degrees: float, altitude_degrees: float) -> str:
        """Move mount to specified azimuth and altitude coordinates"""
        # Convert degrees to steps
        azimuth_steps = self.degrees_to_steps(azimuth_degrees, True)
        altitude_steps = self.degrees_to_steps(altitude_degrees, False)
        
        # Send movement commands
        az_response = self.move_azimuth(azimuth_steps)
        al_response = self.move_altitude(altitude_steps)
        
        return f"Azimuth: {az_response}\nAltitude: {al_response}"
    
    def home_mount(self) -> str:
        """Move mount to home position (0,0)"""
        return self.send_command("HOME")
    
    def stop_mount(self) -> str:
        """Stop all movement"""
        return self.send_command("STOP")
    
    def degrees_to_steps(self, degrees: float, is_azimuth: bool, minutes: float = 0, seconds: float = 0) -> int:
        """Convert degrees, minutes, and seconds to motor steps"""
        total_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if is_azimuth:
            return int((total_degrees / 360.0) * self.AZIMUTH_MAX_STEPS)
        else:
            return int((total_degrees / 90.0) * self.ALTITUDE_MAX_STEPS)

    def steps_to_degrees(self, steps: int, is_azimuth: bool) -> tuple:
        """Convert motor steps to (degrees, minutes, seconds) tuple"""
        if is_azimuth:
            total_degrees = float(steps) * 360.0 / self.AZIMUTH_MAX_STEPS
        else:
            total_degrees = float(steps) * 90.0 / self.ALTITUDE_MAX_STEPS
        deg = int(total_degrees)
        min_ = int((total_degrees - deg) * 60)
        sec = (total_degrees - deg - min_ / 60.0) * 3600.0
        return (deg, min_, sec)
    
    def connect_stellarium(self, host: str = 'localhost', port: int = 10001) -> bool:
        """Connect to Stellarium's Telescope Control plugin"""
        try:
            self.stellarium_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.stellarium_socket.connect((host, port))
            self.stellarium_connected = True
            print(f"Connected to Stellarium on {host}:{port}")
            return True
        except socket.error as e:
            print(f"Failed to connect to Stellarium: {e}")
            self.stellarium_connected = False
            return False
    
    def read_stellarium_coordinates(self) -> Optional[Tuple[float, float]]:
        """Read current telescope coordinates from Stellarium"""
        if not self.stellarium_connected:
            return None
        
        try:
            # Send request for current coordinates
            self.stellarium_socket.send(b"GET_COORDS\n")
            
            # Read response
            response = self.stellarium_socket.recv(1024).decode().strip()
            
            # Parse coordinates (format: "AZ:123.45,ALT:67.89")
            if "AZ:" in response and "ALT:" in response:
                az_part = response.split("AZ:")[1].split(",")[0]
                alt_part = response.split("ALT:")[1]
                
                azimuth = float(az_part)
                altitude = float(alt_part)
                
                return (azimuth, altitude)
            
        except socket.error as e:
            print(f"Error reading from Stellarium: {e}")
            self.stellarium_connected = False
        
        return None
    
    def auto_track(self, update_interval: float = 1.0):
        """Automatically track Stellarium coordinates"""
        if not self.connected:
            print("Arduino not connected")
            return
        
        if not self.stellarium_connected:
            print("Stellarium not connected")
            return
        
        print("Starting auto-tracking mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                coords = self.read_stellarium_coordinates()
                if coords:
                    azimuth, altitude = coords
                    print(f"Target: AZ={azimuth:.2f}°, ALT={altitude:.2f}°")
                    
                    # Move mount to coordinates
                    self.move_to_coordinates(azimuth, altitude)
                
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\nAuto-tracking stopped")
            self.stop_mount()

def float_to_dms(deg_float):
    deg = int(deg_float)
    min_ = int((deg_float - deg) * 60)
    sec = (deg_float - deg - min_ / 60.0) * 3600.0
    return deg, min_, sec


def interpret_ascom_command(cmd):
    cmd = cmd.strip()
    if cmd.startswith(':GR'):  # Get RA
        return 'Get Right Ascension (RA)'
    elif cmd.startswith(':GD'):  # Get Dec
        return 'Get Declination (Dec)'
    elif cmd.startswith(':GA'):  # Get Azimuth
        return 'Get Azimuth'
    elif cmd.startswith(':GZ'):  # Get Altitude
        return 'Get Altitude'
    elif cmd.startswith(':MS'):  # Move to position
        return 'Move to position'
    elif cmd.startswith(':Q'):  # Stop
        return 'Stop motion'
    elif cmd.startswith(':CM'):  # Sync
        return 'Sync to current position'
    elif cmd.startswith(':Q'):  # Stop
        return 'Stop motion'
    elif cmd.startswith(':U'):  # Move North
        return 'Move North'
    elif cmd.startswith(':D'):  # Move South
        return 'Move South'
    elif cmd.startswith(':L'):  # Move East
        return 'Move East'
    elif cmd.startswith(':R'):  # Move West
        return 'Move West'
    # Add more as needed
    return None

def parse_j2000_coords(data_str):
    import re
    # Try to find two floats (RA, Dec) in the string
    matches = re.findall(r'([-+]?\d*\.\d+|\d+)', data_str)
    if len(matches) >= 2:
        try:
            ra = float(matches[0])
            dec = float(matches[1])
            ra_d, ra_m, ra_s = float_to_dms(ra)
            dec_d, dec_m, dec_s = float_to_dms(dec)
            print(f"[DEBUG] J2000: RA = {ra:.6f} ({ra_d}° {ra_m}' {ra_s:.2f}\"), Dec = {dec:.6f} ({dec_d}° {dec_m}' {dec_s:.2f}\")")
        except Exception as e:
            print(f"[DEBUG] Could not parse as floats: {e}")


def stellarium_tcp_listener(host='0.0.0.0', port=10001):
    print(f"[DEBUG] Starting TCP listener on {host}:{port} for Stellarium (J2000 coordinates)...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"[DEBUG] Listening for Stellarium connections on port {port}...")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"[DEBUG] Connection from {addr}")
            with client_socket:
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        print(f"[DEBUG] Connection from {addr} closed.")
                        break
                    try:
                        data_str = data.decode('utf-8', errors='replace').strip()
                        print(f"[DEBUG] Raw data: {data_str!r}")
                        parse_j2000_coords(data_str)
                    except Exception as e:
                        print(f"[DEBUG] Could not decode or parse data: {e}")
    except KeyboardInterrupt:
        print("[DEBUG] TCP listener stopped by user.")
    finally:
        server_socket.close()
        print("[DEBUG] TCP listener closed.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stellarium Mount Interface")
    parser.add_argument('--listen', action='store_true', help='Start TCP listener for Stellarium debug')
    args = parser.parse_args()

    if args.listen:
        stellarium_tcp_listener()
        return

    # Initialize interface
    interface = StellariumMountInterface()
    
    # Connect to Arduino
    if not interface.connect_arduino():
        print("Failed to connect to Arduino. Please check:")
        print("1. Arduino is connected and powered")
        print("2. Correct COM port is specified")
        print("3. Arduino sketch is uploaded")
        return
    
    try:
        while True:
            print("\nStellarium Mount Controller")
            print("1. Get status")
            print("2. Move to coordinates")
            print("3. Move azimuth")
            print("4. Move altitude")
            print("5. Home mount")
            print("6. Stop movement")
            print("7. Auto-track Stellarium")
            print("8. Exit")
            
            choice = input("Enter choice (1-8): ").strip()
            
            if choice == '1':
                status = interface.get_status()
                print(f"Status: {status}")
                
            elif choice == '2':
                try:
                    az = float(input("Enter azimuth (degrees): "))
                    alt = float(input("Enter altitude (degrees): "))
                    result = interface.move_to_coordinates(az, alt)
                    print(f"Result: {result}")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '3':
                try:
                    steps = int(input("Enter azimuth steps: "))
                    result = interface.move_azimuth(steps)
                    print(f"Result: {result}")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '4':
                try:
                    steps = int(input("Enter altitude steps: "))
                    result = interface.move_altitude(steps)
                    print(f"Result: {result}")
                except ValueError:
                    print("Invalid input")
                    
            elif choice == '5':
                result = interface.home_mount()
                print(f"Result: {result}")
                
            elif choice == '6':
                result = interface.stop_mount()
                print(f"Result: {result}")
                
            elif choice == '7':
                if interface.connect_stellarium():
                    interface.auto_track()
                else:
                    print("Failed to connect to Stellarium")
                    
            elif choice == '8':
                break
                
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    
    finally:
        interface.disconnect_arduino()

if __name__ == "__main__":
    main() 