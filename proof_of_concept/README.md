# Proof of Concept

This folder demonstrates running the full algorithm in "real time" on a pre-recorded flight, and generates a map of the expected route compared with the actual groud truth recorded by the GPS on the drone.

## Usage

The pipeline can be run as follows:

```
python3 proof_of_concept.py LOG_FILE VIDEO_FILE VIDEO_OFFSET
```

For example:

```
python3 proof_of_concept.py "/home/james/data/videos/sample5/2019-09-10 16-18-38.tlog" "/home/james/data/videos/sample5/full_video.mp4" 1568122126
```

You can add an option `--start_offset` argument, which specifies a number of seconds into the video at which replay should start.

## Configuration

A configuration file is required. An example is below:

```json
{
    "ground_altitude": 120,
    "height": 0.05,
    "patch_size": 512,
    "stride_size": 128,
    "url": "https://api.maptiler.com/tiles/satellite-v2/{z}/{x}/{y}.jpg?key=KEY",
    "width": 0.05,
    "zoom": 16
}
```

## Outputs

The proof of concept produces two outputs:

1) A CSV file (`output.csv`) containing the Ground Truth and Predicted locations.
2) A KML file (`output.kml`) containing tracks for the Ground Truth, Uncorrected Predicted locations (the raw output from the model) and the Corrected Predicted locations (the outputs corrected for camera attitude).

You can get a live updating view in Google Earth Pro by adding the KML as a Network Link, and the setting a Refresh Rate to a few seconds. The model tends to take ~15-20 seconds to process a frame, so there will only be occasional updates. The proof of concept tool processes the input in "real time" - so if it takes 20 seconds to process a frame, the next frame it processes will be 20 seconds later (rather than the next frame).