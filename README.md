# Stellarium Mount Controller

A complete Arduino-based telescope mount controller that interfaces with Stellarium for automated astronomical observations.

## Overview

This project provides:
- **Arduino sketch** for controlling two stepper motors (azimuth and altitude)
- **Python interface** for communication between Stellarium and Arduino
- **Complete wiring diagrams** and setup instructions
- **Serial command protocol** for mount control

## Hardware Requirements

- [Arduino Uno R3](https://store-usa.arduino.cc/products/arduino-uno-rev3)
- [2x ELEGOO 28BYJ-48 ULN2003 5V Stepper Motors](https://www.amazon.com/ELEGOO-28BYJ-48-ULN2003-Stepper-Arduino/dp/B01CP18J4A/)
- USB cable for Arduino
- Power supply (5V for motors)
- Telescope mount assembly

## Quick Start

### 1. Hardware Setup

1. **Wire the motors** according to `src/WIRING.md`
2. **Power the system** - Arduino via USB, motors via 5V supply
3. **Mount the motors** to your telescope assembly

### 2. Arduino Setup

1. **Upload the sketch**:
   - Open `src/StellariumMount.ino` in Arduino IDE
   - Select your Arduino board and port
   - Upload the sketch

2. **Test the motors**:
   - Open Serial Monitor (9600 baud)
   - Send test commands:
     ```
     AZ,100    # Move azimuth 100 steps
     AL,50     # Move altitude 50 steps
     STATUS    # Check position
     HOME      # Return to home
     ```

### 3. Python Interface Setup

1. **Install dependencies**:
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **Run the interface**:
   ```bash
   python stellarium_interface.py
   ```

3. **Configure COM port** (if needed):
   - Edit the port in `stellarium_interface.py` (default: 'COM3')
   - On Linux/Mac, use '/dev/ttyUSB0' or similar

## Features

### Arduino Controller
- **Dual motor control** for azimuth (0-360°) and altitude (0-90°)
- **Precise stepping** with 2048 steps per revolution
- **Serial communication** for remote control
- **Safety limits** and position tracking
- **Smooth operation** with 8-step sequence

### Python Interface
- **Serial communication** with Arduino
- **Coordinate conversion** between degrees and steps
- **Stellarium integration** (requires Telescope Control plugin)
- **Auto-tracking mode** for continuous observation
- **Interactive testing** and debugging

### Command Protocol

| Command | Description |
|---------|-------------|
| `AZ,<steps>` | Move azimuth motor to step position |
| `AL,<steps>` | Move altitude motor to step position |
| `STATUS` | Get current position and movement status |
| `HOME` | Move both motors to home position (0,0) |
| `STOP` | Stop all movement |
| `HELP` | Show available commands |

## Stellarium Integration

### Option 1: Direct Python Interface
The Python script can connect to Stellarium's Telescope Control plugin:
1. Enable Telescope Control in Stellarium
2. Configure the plugin for your mount
3. Run the Python interface in auto-tracking mode

### Option 2: Custom Stellarium Plugin
For advanced users, create a custom Stellarium plugin that:
1. Reads telescope coordinates from Stellarium
2. Converts to motor steps
3. Sends commands to Arduino

### Option 3: External Software
Use third-party software like:
- StellariumScope
- ASCOM drivers
- Custom astronomical software

## Configuration

### Motor Parameters
Edit these values in both Arduino and Python code:
```cpp
const int STEPS_PER_REVOLUTION = 2048;  // Adjust for your gear ratio
const int STEP_DELAY = 2;               // Speed control (ms)
```

### Pin Assignments
Change pin numbers in Arduino sketch if needed:
```cpp
#define AZIMUTH_IN1 2   // Azimuth motor pins
#define AZIMUTH_IN2 3
#define AZIMUTH_IN3 4
#define AZIMUTH_IN4 5

#define ALTITUDE_IN1 6  // Altitude motor pins
#define ALTITUDE_IN2 7
#define ALTITUDE_IN3 8
#define ALTITUDE_IN4 9
```

## Troubleshooting

### Common Issues

1. **Motors not moving**:
   - Check wiring connections
   - Verify power supply
   - Test with simple commands

2. **Serial communication errors**:
   - Check COM port selection
   - Ensure Arduino is connected
   - Verify baud rate (9600)

3. **Inaccurate positioning**:
   - Calibrate steps per revolution
   - Check gear ratios
   - Verify motor direction

4. **Stellarium connection issues**:
   - Enable Telescope Control plugin
   - Check network settings
   - Verify plugin configuration

### Testing Commands

Test each component individually:
```bash
# Test Arduino communication
echo "STATUS" > /dev/ttyUSB0

# Test motor movement
echo "AZ,100" > /dev/ttyUSB0
echo "AL,50" > /dev/ttyUSB0

# Test Python interface
python -c "from stellarium_interface import StellariumMountInterface; i = StellariumMountInterface(); print(i.get_status())"
```

## Advanced Features

### Custom Calibration
Implement custom calibration routines:
```python
# Example: Calibrate steps per degree
def calibrate_motor(interface, motor_type):
    # Move known distance
    # Measure actual movement
    # Calculate correction factor
    pass
```

### Safety Features
Add safety mechanisms:
- Limit switches for end stops
- Emergency stop functionality
- Position validation
- Overload protection

### Performance Optimization
Improve performance:
- Adjust step delay for speed vs. accuracy
- Implement acceleration ramping
- Add position interpolation
- Optimize serial communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the wiring diagram
3. Test with simple commands first
4. Check Arduino and Python documentation

## Acknowledgments

- Stellarium team for the excellent astronomy software
- Arduino community for hardware support
- ELEGOO for quality stepper motors 