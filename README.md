# RC Drift Gyro Stabilizer

An advanced gyro-based steering stabilization system for RC drift cars, designed using the Raspberry Pi RP2040 and MPU6050 gyroscope. This project integrates precise steering corrections, remote control functionality, and visual feedback using an RGB LED.

---

## Features

- **Gyroscope Integration (MPU6050):** Provides real-time stabilization to enhance RC drift performance.
- **Servo Steering Control:** Smooth and precise adjustments to the steering angle.
- **Remote Control Input:** Seamlessly integrates with standard RC remote signals.
- **RGB LED Feedback:** Visual indicators for system states:
  - **Red:** System boot-up.
  - **Blue:** Gyro-based stabilization active.
  - **Green:** Remote control input active.
- **Noise Reduction:** Filters and calibration for smooth operation and reduced jitter.

---

## How It Works

1. **Gyroscope Calibration:**
   - On startup, the gyroscope (MPU6050) is calibrated to minimize offset.
   
2. **Remote and Gyro Control:**
   - The system prioritizes input from the remote control.
   - When remote input is inactive, the gyro takes over to stabilize the steering.

3. **Visual Feedback:**
   - The RGB LED indicates the current system state, helping to debug and monitor the system.

---

## Hardware Requirements

- **Raspberry Pi RP2040-Zero** (or similar)
- **MPU6050 Gyroscope**
- **Servo Motor** (for steering)
- **RGB LED** (NeoPixel)
- **RC Remote Receiver**

---

## Installation

1. Clone this repository:
Upload the code to your RP2040 board using a MicroPython-compatible IDE like Thonny.

Connect the hardware as described in the circuit diagram (refer to docs/circuit_diagram.png if included).

Power up the system and test.

Circuit Diagram
To connect the hardware, follow this pin configuration:

Component	Pin on RP2040
MPU6050 SDA	GPIO 4
MPU6050 SCL	GPIO 5
Servo Signal	GPIO 15
RGB LED	GPIO 16
Remote Signal	GPIO 14
Usage
Power up the system.
Use your RC remote to control the steering. The system will prioritize remote input.
If the remote input is inactive, the gyroscope will automatically stabilize the steering.
Future Improvements
Add support for additional sensors to further enhance stability.
Implement a mobile app for real-time adjustments and diagnostics.
Optimize the gyro filtering for even smoother operation.
License
This project is licensed under the MIT License. See the LICENSE file for more information.

Contribution
Contributions are welcome! Feel free to submit a pull request or open an issue for suggestions or bug reports.

Author
Developed with 💡 and 💻 by Mahyar heydari.
