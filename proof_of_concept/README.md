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