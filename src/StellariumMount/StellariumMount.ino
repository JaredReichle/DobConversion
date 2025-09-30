/*
 * Stellarium Mount Controller
 * Controls two stepper motors for azimuth and altitude movement
 * Interfaces with Stellarium via serial communication
 * 
 * Hardware:
 * - Arduino Uno R3
 * - 2x ELEGOO 28BYJ-48 ULN2003 5V Stepper Motors
 * 
 * Motor Specifications:
 * - 28BYJ-48 stepper motor with ULN2003 driver
 * - 5V operation
 * - 2048 steps per revolution (with gear reduction)
 * - 64 steps per motor revolution
 */

// Pin definitions for Azimuth motor (Motor 1)
#define AZIMUTH_IN1 2
#define AZIMUTH_IN2 3
#define AZIMUTH_IN3 4
#define AZIMUTH_IN4 5

// Pin definitions for Altitude motor (Motor 2)
#define ALTITUDE_IN1 6
#define ALTITUDE_IN2 7
#define ALTITUDE_IN3 8
#define ALTITUDE_IN4 9

// Motor control arrays
int azimuthPins[4] = {AZIMUTH_IN1, AZIMUTH_IN2, AZIMUTH_IN3, AZIMUTH_IN4};
int altitudePins[4] = {ALTITUDE_IN1, ALTITUDE_IN2, ALTITUDE_IN3, ALTITUDE_IN4};

// Stepping sequence for 28BYJ-48 motor (8-step sequence for smoother operation)
int stepSequence[8][4] = {
  {1, 0, 0, 0},
  {1, 1, 0, 0},
  {0, 1, 0, 0},
  {0, 1, 1, 0},
  {0, 0, 1, 0},
  {0, 0, 1, 1},
  {0, 0, 0, 1},
  {1, 0, 0, 1}
};

// Motor state variables
int azimuthStep = 0;
int altitudeStep = 0;
int azimuthTarget = 0;
int altitudeTarget = 0;
bool azimuthMoving = false;
bool altitudeMoving = false;

// Motor test flags
bool testAzimuthOnly = false;
bool testAltitudeOnly = false;
bool testBothMotors = true;  // Default to testing both motors

// Movement parameters
const int STEPS_PER_REVOLUTION = 2048;  // Full revolution including gear reduction
const int AZIMUTH_MAX_STEPS = STEPS_PER_REVOLUTION;  // 360 degrees
const int ALTITUDE_MAX_STEPS = STEPS_PER_REVOLUTION / 2;  // 180 degrees (0-90 degrees)
const int STEP_DELAY = 2;  // Delay between steps in milliseconds

// Serial communication
String inputString = "";
bool stringComplete = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Stellarium Mount Controller Ready");
  Serial.println("Commands:");
  Serial.println("  AZ,<steps> - Move azimuth motor");
  Serial.println("  AL,<steps> - Move altitude motor");
  Serial.println("  STATUS - Get current position");
  Serial.println("  HOME - Move to home position");
  Serial.println("  STOP - Stop all movement");
  Serial.println("  TEST_AZ - Test azimuth motor only");
  Serial.println("  TEST_AL - Test altitude motor only");
  Serial.println("  TEST_BOTH - Test both motors (default)");
  Serial.println("  TEST_MODE - Show current test mode");
  
  // Initialize motor pins
  for (int i = 0; i < 4; i++) {
    pinMode(azimuthPins[i], OUTPUT);
    pinMode(altitudePins[i], OUTPUT);
    digitalWrite(azimuthPins[i], LOW);
    digitalWrite(altitudePins[i], LOW);
  }
  
  // Initialize input string
  inputString.reserve(50);
}

void loop() {
  // Handle serial commands
  if (stringComplete) {
    processCommand(inputString);
    inputString = "";
    stringComplete = false;
  }
  
  // Move motors if needed (respecting test mode flags)
  if (azimuthMoving && (testAzimuthOnly || testBothMotors)) {
    moveAzimuthMotor();
  }
  
  if (altitudeMoving && (testAltitudeOnly || testBothMotors)) {
    moveAltitudeMotor();
  }
  
  // Small delay to prevent overwhelming the system
  delay(1);
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void processCommand(String command) {
  command.trim();
  command.toUpperCase();
  
  if (command.startsWith("AZ,")) {
    // Azimuth movement command
    int steps = command.substring(3).toInt();
    moveAzimuthTo(steps);
    Serial.print("AZIMUTH: Moving to step ");
    Serial.println(steps);
  }
  else if (command.startsWith("AL,")) {
    // Altitude movement command
    int steps = command.substring(3).toInt();
    moveAltitudeTo(steps);
    Serial.print("ALTITUDE: Moving to step ");
    Serial.println(steps);
  }
  else if (command == "STATUS") {
    // Report current position
    Serial.print("STATUS: AZ=");
    Serial.print(azimuthStep);
    Serial.print(", AL=");
    Serial.print(altitudeStep);
    Serial.print(", AZ_MOVING=");
    Serial.print(azimuthMoving ? "1" : "0");
    Serial.print(", AL_MOVING=");
    Serial.print(altitudeMoving ? "1" : "0");
    Serial.print(", TEST_MODE=");
    if (testAzimuthOnly) {
      Serial.println("AZ_ONLY");
    } else if (testAltitudeOnly) {
      Serial.println("AL_ONLY");
    } else if (testBothMotors) {
      Serial.println("BOTH");
    }
  }
  else if (command == "HOME") {
    // Move to home position
    moveAzimuthTo(0);
    moveAltitudeTo(0);
    Serial.println("HOME: Moving to home position");
  }
  else if (command == "STOP") {
    // Stop all movement
    azimuthMoving = false;
    altitudeMoving = false;
    Serial.println("STOP: All movement stopped");
  }
  else if (command == "HELP") {
    // Show help
    Serial.println("Available commands:");
    Serial.println("  AZ,<steps> - Move azimuth motor to step position");
    Serial.println("  AL,<steps> - Move altitude motor to step position");
    Serial.println("  STATUS - Get current position and movement status");
    Serial.println("  HOME - Move both motors to home position (0,0)");
    Serial.println("  STOP - Stop all movement");
    Serial.println("  TEST_AZ - Test azimuth motor only");
    Serial.println("  TEST_AL - Test altitude motor only");
    Serial.println("  TEST_BOTH - Test both motors (default)");
    Serial.println("  TEST_MODE - Show current test mode");
    Serial.println("  HELP - Show this help message");
  }
  else if (command == "TEST_AZ") {
    // Set test mode to azimuth only
    testAzimuthOnly = true;
    testAltitudeOnly = false;
    testBothMotors = false;
    Serial.println("TEST_MODE: Azimuth motor only");
  }
  else if (command == "TEST_AL") {
    // Set test mode to altitude only
    testAzimuthOnly = false;
    testAltitudeOnly = true;
    testBothMotors = false;
    Serial.println("TEST_MODE: Altitude motor only");
  }
  else if (command == "TEST_BOTH") {
    // Set test mode to both motors
    testAzimuthOnly = false;
    testAltitudeOnly = false;
    testBothMotors = true;
    Serial.println("TEST_MODE: Both motors");
  }
  else if (command == "TEST_MODE") {
    // Show current test mode
    Serial.print("TEST_MODE: ");
    if (testAzimuthOnly) {
      Serial.println("Azimuth motor only");
    } else if (testAltitudeOnly) {
      Serial.println("Altitude motor only");
    } else if (testBothMotors) {
      Serial.println("Both motors");
    }
  }
  else {
    Serial.print("ERROR: Unknown command '");
    Serial.print(command);
    Serial.println("'. Type HELP for available commands.");
  }
}

void moveAzimuthTo(int target) {
  azimuthTarget = constrain(target, 0, AZIMUTH_MAX_STEPS);
  azimuthMoving = true;
}

void moveAltitudeTo(int target) {
  altitudeTarget = constrain(target, 0, ALTITUDE_MAX_STEPS);
  altitudeMoving = true;
}

void moveAzimuthMotor() {
  if (azimuthStep < azimuthTarget) {
    // Move clockwise
    azimuthStep++;
    stepMotor(azimuthPins, 1);
  }
  else if (azimuthStep > azimuthTarget) {
    // Move counter-clockwise
    azimuthStep--;
    stepMotor(azimuthPins, -1);
  }
  else {
    // Reached target
    azimuthMoving = false;
    Serial.println("AZIMUTH: Target reached");
  }
}

void moveAltitudeMotor() {
  if (altitudeStep < altitudeTarget) {
    // Move up
    altitudeStep++;
    stepMotor(altitudePins, 1);
  }
  else if (altitudeStep > altitudeTarget) {
    // Move down
    altitudeStep--;
    stepMotor(altitudePins, -1);
  }
  else {
    // Reached target
    altitudeMoving = false;
    Serial.println("ALTITUDE: Target reached");
  }
}

void stepMotor(int motorPins[4], int direction) {
  static int currentStep = 0;
  
  if (direction > 0) {
    currentStep = (currentStep + 1) % 8;
  } else {
    currentStep = (currentStep - 1 + 8) % 8;
  }
  
  // Apply step sequence to motor
  for (int i = 0; i < 4; i++) {
    digitalWrite(motorPins[i], stepSequence[currentStep][i]);
  }
  
  delay(STEP_DELAY);
}

// Utility function to convert degrees to steps
int degreesToSteps(float degrees, bool isAzimuth) {
  if (isAzimuth) {
    return (int)((degrees / 360.0) * AZIMUTH_MAX_STEPS);
  } else {
    return (int)((degrees / 90.0) * ALTITUDE_MAX_STEPS);
  }
}

// Utility function to convert steps to degrees
float stepsToDegrees(int steps, bool isAzimuth) {
  if (isAzimuth) {
    return (float)steps * 360.0 / AZIMUTH_MAX_STEPS;
  } else {
    return (float)steps * 90.0 / ALTITUDE_MAX_STEPS;
  }
} 