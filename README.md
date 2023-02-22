# Dstl (Team 1)

Team from the Defence Science and Technology Laboratory (Dstl) in the UK.

## Problem

The challenge we were tackling was the Small UAV Visual Navigation problem, which is to develop an alternative approach to autonomous UAV navigation in a GPS denied environment, for example where there is GPS jamming.

## Solution

Our solution is to use the camera available on the drone to georeference the drones current location to a reference map (for example satellite imagery). This will give an (approximate) location, which can be used in place of GPS. Whilst it won't have the same accuracy as GPS, it should provide enough accuracy to navigate back to a safe space or even complete wide area reconnaisance missions.

The georeferencing uses a [Siamese neural network](https://en.wikipedia.org/wiki/Siamese_neural_network) model to enable georeferencing between images taken at different angles, at different times of day/year, and zoom levels. The model was trained on the [LandCover.ai](https://landcover.ai.linuxpolska.com/) dataset. This produces a number of predictions and probabilities, which can be combined with previously known positions to help choose the most likely location.

One key advantage of this approach is that there is no error propagation between iterations, so should the model prediction produce a bad location, this will not negatively affect future predictions.

### Pseudocode

The pseudo code below outlines our solution workflow.

```python
# Use our start location (i.e. where we lost GPS signal) as our initial starting point
location = start_location

# Keep track of previous locations
previous_locations = [location]

# Whilst we have new data, retrieve the latest image and sensor data (e.g. altimeter, yaw, pitch, roll)
while image, drone_metadata = get_latest_data():
    # Get reference mapping for a reasonable area around our last known location
    map = get_reference_map(location, search_radius)

    # This step is a future improvement, to project the image from the camera into an orthogonal (i.e. overhead) image
    # image = correct_persepective(image, drone_metadata)

    # Use the neural network to determine the location, weighting based on the last 5 locations
    image_location = determine_location_nn(image, map, previous_locations[-5:])

    # Use sensor data (e.g. sensor direction) to calculate offset of the image compared to drone and account for this
    drone_location = calculate_offset(image_location, drone_metadata)

    # Update list of previous locations
    location = drone_location
    previous_locations.append(location)
```

### Caveats and Known Limitations

The following are a list of caveats and known limitations to our approach:

* Our approach is likely to work best on "feature rich" areas where there are lots of features within the imagery to match to the reference map. This could be roads, buildings, waterways, field boundaries or any other unique feature. Where the image is very generic (e.g. a large empty field, or a single straight road with no other features) then the approach will struggle. However, as errors don't propagate with our approach, as soon as there are discernible features the approach will be able to locate the drone again regardless of the loss of location.

### Future Work

The following is a list of ideas for improving the approach further in the future:

* Rectification of images (i.e. correcting for perspective) prior to feeding them into the neural network
* Improving the training data to include a wider range of perspectives and weather conditions

## Other Attempted Approaches

Below are some of the other approaches that we tried during the Hackathon, that were abandoned either due to time constraints or deciding they weren't suitable for the problem.

### Segmentation

We looked at trying to simplify the images by segmenting them into land cover usage (road, water, buildings, other). A write up of this approach can be seen in the `segmentation` folder [here](segmentation/README.md).

### Visual Inertial Navigation and SLAM (Simultaneous Localisation and Mapping)

We briefly looked at getting some existing Visual Inertial Navigation and SLAM tools running, with the idea of feeding our data in and seeing what we could get out of them. However, they proved difficult to get working on our laptops and once we had it wasn't easy to feed our data into them tools so we decided to abandon this approach.