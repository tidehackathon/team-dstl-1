# Dstl (Team 1)

Team from the Defence Science and Technology Laboratory (Dstl) in the UK.

## Solution workflow

The pseudo code below outlines our current solution workflow. More detail about the steps below will be added soon...

```
location = start_location
previous_locations = []

while image, drone_metadata = get_latest_data():
    previous_locations.append(location)

    map = get_reference_map(location, search_radius)

    # image = correct_persepective(image, drone_metadata)

    image_location = determine_location_nn(image, map, previous_locations[-5:])
    drone_location = calculate_offset(image_location, drone_metadata)

    location = drone_location
```

## Infrastructure

The following components are created as part of our infrastructure, which is hosted on AWS. The infrastructure is defined using Terraform to provide IaC.

* `videos` bucket - an S3 bucket containing the original raw data
* `frames` bucket - an S3 bucket containing frames extracted from each video
* `ref` bucket - an S3 bucket containing reference data, including reference mapping
