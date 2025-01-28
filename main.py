from machine import Pin, PWM, I2C, time_pulse_us
import neopixel
from time import sleep

# ------ RGB LED Configuration ------
led_pin = Pin(16)  # Pin for the RGB LED
num_leds = 1
np = neopixel.NeoPixel(led_pin, num_leds)

def set_led_color(color):
    """Set the color of the RGB LED."""
    np[0] = color
    np.write()

# ------ Servo Configuration ------
servo = PWM(Pin(15))  # Pin for the servo signal
servo.freq(50)

# Previous servo angle
current_angle = 90

def set_servo_angle(target_angle):
    """Smoothly adjust the servo angle."""
    global current_angle
    # Limit the angle to the valid range
    target_angle = max(30, min(150, target_angle))
    
    # Gradual adjustment of the angle
    if abs(target_angle - current_angle) > 2:  # Change only if the difference is greater than 2 degrees
        current_angle += (target_angle - current_angle) * 0.1  # Smooth transition
        duty = int(500 + (current_angle / 180) * 2000)
        servo.duty_u16(int(duty * 65535 / 20000))
        print(f"Servo set to angle: {current_angle:.2f}")

# ------ Sensitivity and Dead Zone Configuration ------
gain_left = 0.8  # Gyro sensitivity for left turn (higher for left)
gain_right = 0.6  # Gyro sensitivity for right turn
dead_zone_gyro = 50  # Gyro dead zone to filter out noise
dead_zone_remote = 0  # Remote signal dead zone
max_correction_left = 80  # Max correction angle by the gyro for left turn
max_correction_right = 55  # Max correction angle by the gyro for right turn

# ------ I2C and Gyro Configuration ------
i2c = I2C(0, scl=Pin(5), sda=Pin(4))  # I2C pins for MPU6050
MPU6050_ADDR = 0x68
i2c.writeto_mem(MPU6050_ADDR, 0x6B, b'\x00')  # Activate MPU6050

def read_raw_data(register):
    """Read raw data from the MPU6050."""
    data = i2c.readfrom_mem(MPU6050_ADDR, register, 2)
    value = (data[0] << 8) | data[1]
    if value > 32768:
        value -= 65536
    return value

# ------ Exponential Moving Average (EMA) Filter for Gyro ------
alpha = 0.2  # Smoothing factor (lower value = smoother data)
filtered_gyro = 0

def apply_gyro_filter(new_value):
    """Apply EMA filter to gyro data."""
    global filtered_gyro
    filtered_gyro = alpha * new_value + (1 - alpha) * filtered_gyro
    return filtered_gyro

# ------ Gyro Calibration ------
gyro_offset = 0

def calibrate_gyro():
    """Calibrate the gyro to reduce offset."""
    global gyro_offset
    samples = 100
    total = 0
    print("Calibrating gyro...")
    for _ in range(samples):
        total += read_raw_data(0x47)  # Read Z-axis data
        sleep(0.01)
    gyro_offset = total / samples
    print(f"Gyro calibration completed! Offset: {gyro_offset}")

# ------ Remote Signal Configuration ------
remote_signal = Pin(14, Pin.IN)  # Pin for the remote signal input

# Calibrate the gyro on startup
calibrate_gyro()

# Set RGB LED to red on system startup
set_led_color((255, 0, 0))  # Red color

# ------ Main Loop ------
while True:
    try:
        # Measure the pulse width from the remote
        pulse_width = time_pulse_us(remote_signal, 1, 20000)  # Max time: 20ms

        if 1000 <= pulse_width <= 2000:  # If the remote signal is valid
            set_led_color((0, 255, 0))  # Green for remote input
            print(f"Remote Pulse Width: {pulse_width} µs")

            # Convert pulse width to angle
            angle_from_remote = (pulse_width - 1000) * 180 / 1000

            # Apply dead zone for remote signal
            if abs(angle_from_remote - current_angle) < dead_zone_remote:
                angle_from_remote = current_angle

            # Add gyro correction to the remote angle
            gyro_z = read_raw_data(0x47) - gyro_offset
            if abs(gyro_z) < dead_zone_gyro:
                gyro_z = 0  # Ignore small changes (noise)

            filtered_gyro_z = apply_gyro_filter(gyro_z)  # Apply EMA filter

            # Adjust correction separately for left and right turns
            if filtered_gyro_z > 0:  # Turning right
                correction = gain_right * (filtered_gyro_z / 131.0)
                correction = max(-max_correction_right, min(max_correction_right, correction))
            else:  # Turning left
                correction = gain_left * (filtered_gyro_z / 131.0)
                correction = max(-max_correction_left, min(max_correction_left, correction))

            # Combine gyro correction with remote input
            final_angle = angle_from_remote - correction

            # Apply the final angle to the servo
            set_servo_angle(final_angle)
            print(f"Remote Angle: {angle_from_remote:.2f}, Gyro Correction: {correction:.2f}, Final Angle: {final_angle:.2f}")
        else:
            set_led_color((0, 0, 255))  # Blue for gyro control
            print("Remote inactive, using gyro control")
            
            # Full control by the gyro
            gyro_z = read_raw_data(0x47) - gyro_offset
            if abs(gyro_z) < dead_zone_gyro:
                gyro_z = 0  # Ignore small changes (noise)

            filtered_gyro_z = apply_gyro_filter(gyro_z)  # Apply EMA filter

            # Adjust correction separately for left and right turns
            if filtered_gyro_z > 0:  # Turning right
                correction = gain_right * (filtered_gyro_z / 131.0)
                correction = max(-max_correction_right, min(max_correction_right, correction))
            else:  # Turning left
                correction = gain_left * (filtered_gyro_z / 131.0)
                correction = max(-max_correction_left, min(max_correction_left, correction))

            new_angle = 90 - correction

            # Apply the angle to the servo
            set_servo_angle(new_angle)
            print(f"Gyro Z: {gyro_z:.2f}, Filtered: {filtered_gyro_z:.2f}, Correction: {correction:.2f}, Servo Angle: {new_angle:.2f}")
    except Exception as e:
        print(f"Error: {e}")

    sleep(0.02)  # Short delay for smoother operation
