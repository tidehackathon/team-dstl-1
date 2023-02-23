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