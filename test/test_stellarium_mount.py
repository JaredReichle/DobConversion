import serial
import time

# Update this to match your Arduino's COM port (e.g., 'COM3' on Windows, '/dev/ttyACM0' on Linux)
SERIAL_PORT = 'COM3'
BAUD_RATE = 9600

def print_available_commands():
    print("\nAvailable commands:")
    print("  AZ,<steps>     - Move azimuth motor to step position")
    print("  AL,<steps>     - Move altitude motor to step position")
    print("  STATUS         - Get current position and movement status")
    print("  HOME           - Move both motors to home position (0,0)")
    print("  STOP           - Stop all movement")
    print("  TEST_AZ        - Test azimuth motor only")
    print("  TEST_AL        - Test altitude motor only")
    print("  TEST_BOTH      - Test both motors (default)")
    print("  TEST_MODE      - Show current test mode")
    print("  HELP           - Show this help message")
    print("  exit           - Exit this script\n")

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for Arduino to reset
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud.")
        print_available_commands()
        print("Type commands to send to the Arduino. Type 'exit' to quit.\n")

        # Read initial Arduino output
        while ser.in_waiting:
            print(ser.readline().decode(errors='ignore').strip())

        while True:
            cmd = input(">>> ")
            if cmd.lower() == 'exit':
                break
            ser.write((cmd + '\n').encode())
            time.sleep(0.1)
            # Read all available lines from Arduino
            while ser.in_waiting:
                print(ser.readline().decode(errors='ignore').strip())
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        try:
            ser.close()
        except:
            pass

if __name__ == '__main__':
    main() 