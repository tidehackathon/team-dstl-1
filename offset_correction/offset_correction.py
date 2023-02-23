import numpy as np
import math
from scipy.spatial.transform import Rotation

def correct_offset_rot(uncorrected_lat, uncorrected_lon, yaw, pitch, roll, altitude, altitude_offset, a, b, c):
    # Altitude
    relative_altitude = altitude - altitude_offset

    # Camera Attitude
    camera_pitch = a / 100
    camera_roll = b / 100
    camera_yaw = np.fmod((c / 100), 360)

    # Rotations
    platform_rotation = Rotation.from_euler('ZYX', (yaw, pitch, roll))
    sensor_rotation = Rotation.from_euler('ZYX', (camera_yaw, camera_pitch, camera_roll), degrees=True)

    # Combine rotations
    platform_sensor_rotation = (platform_rotation*sensor_rotation).inv().as_matrix()

    # Extract combined yaw-pitch-roll
    r = Rotation.from_matrix(platform_sensor_rotation)
    combined_angles = r.as_euler("zyx")

    combined_yaw = combined_angles[0]
    combined_pitch = combined_angles[1]

    # Calculate magnitude
    theta = (math.pi / 2) - combined_pitch
    correction_magnitude_meters = relative_altitude * math.tan(theta)
    meter_as_dec_degrees = (1/111111) / math.cos(math.radians(uncorrected_lat))
    correction_magnitude_degrees = correction_magnitude_meters * meter_as_dec_degrees

    # Calculate direction
    correction_direction = (combined_yaw + 180) % 360

    # Calculate corrected lat-lon
    lat_correction = correction_magnitude_degrees * math.cos(correction_direction)
    lon_correction = correction_magnitude_degrees * math.sin(correction_direction)

    corrected_lat = uncorrected_lat + lat_correction
    corrected_lon = uncorrected_lon + lon_correction 

    return corrected_lat, corrected_lon