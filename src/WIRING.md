# Wiring Diagram for Stellarium Mount Controller

## Hardware Components
- Arduino Uno R3
- 2x ELEGOO 28BYJ-48 ULN2003 5V Stepper Motors with driver boards

## Pin Connections

### Azimuth Motor (Motor 1)
Connect the ULN2003 driver board to Arduino pins:
- **IN1** → Arduino Pin 2
- **IN2** → Arduino Pin 3  
- **IN3** → Arduino Pin 4
- **IN4** → Arduino Pin 5
- **VCC** → Arduino 5V
- **GND** → Arduino GND

### Altitude Motor (Motor 2)
Connect the ULN2003 driver board to Arduino pins:
- **IN1** → Arduino Pin 6
- **IN2** → Arduino Pin 7
- **IN3** → Arduino Pin 8
- **IN4** → Arduino Pin 9
- **VCC** → Arduino 5V
- **GND** → Arduino GND

## Power Supply
- Both motors can be powered from the Arduino's 5V supply for testing
- For production use, consider using an external 5V power supply for the motors
- Connect external power supply GND to Arduino GND
- Connect external power supply 5V to motor driver VCC pins

## Physical Mount Setup
1. **Azimuth Motor**: Mount to rotate the entire telescope assembly horizontally (0-360°)
2. **Altitude Motor**: Mount to rotate the telescope vertically (0-90°)
3. Ensure proper gear ratios for your specific mount design
4. Add limit switches if needed for safety

## Testing
1. Upload the Arduino sketch
2. Open Serial Monitor at 9600 baud
3. Test commands:
   - `AZ,100` - Move azimuth motor 100 steps
   - `AL,50` - Move altitude motor 50 steps
   - `STATUS` - Check current position
   - `HOME` - Return to home position
   - `STOP` - Stop all movement

## Stellarium Integration
The Arduino communicates via serial commands that can be interfaced with Stellarium using:
- Stellarium's Telescope Control plugin
- Custom scripts or external software
- Serial communication libraries in various programming languages 