# Offset Correction

Our geolocation from the images tells us where the image is, but we need to correct that location for where the camera is. This can be done by using the attitude of the sensor along with the platform height, and some trigonometry.

Due to the relationship between platform and sensor, the roll must be considered when calculating a directional vector. This is done by converting each set of yaw, pitch and roll to a rotational matrix, combinig the two matrices and converting back. 