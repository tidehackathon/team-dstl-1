import numpy as np
import json
import pandas as pd
import math

def correct_offset(uncorrected_lat, uncorrected_lon, heading, pitch, roll, altitude, altitude_offset, latitude, a, b, c):
    # Altitude sensor is meters above sea level
    # Relative altitude subtracts average elevation (could use a dem)
    relative_altitude = altitude - altitude_offset
    camera_pitch = a / 100
    camera_roll = b / 100
    camera_yaw = np.fmod((c / 100), 360)

    # The camera's attitude is relative to the platform
    combined_pitch = pitch + math.radians(camera_pitch)
    combined_roll = roll + math.radians(camera_roll)
    combined_heading = heading + camera_yaw

    # Calculate theta (pitch relative to vertical down)
    theta = (math.pi / 2) - combined_pitch

    # Calculate magnitude of correction in meters (Pythagoras)
    correction_magnitude_meters = relative_altitude * math.tan(theta)

    # We need to translate the predicted location in the opposite direction to heading
    # Remember to modulo 360 
    correction_direction = (combined_heading + 180) % 360

    # Approximation of meters in WGS84
    meter_as_dec_degrees = (1/111111) / math.cos(math.radians(latitude))

    correction_magnitude_degrees = correction_magnitude_meters * meter_as_dec_degrees

    # We need the vector components of heading and magnitude, this deviates from most formulae
    # Because 0 degrees is x=0 y=1 and degrees increase clockwise, unlike standard cartesians coords
    # x, y = mag * sin(heading), mag * cos(heading)
    lat_correction = correction_magnitude_degrees * math.cos(correction_direction)
    lon_correction = correction_magnitude_degrees * math.sin(correction_direction)

    corrected_lat = uncorrected_lat + lat_correction
    corrected_lon = uncorrected_lon + lon_correction 

    return corrected_lat, corrected_lon