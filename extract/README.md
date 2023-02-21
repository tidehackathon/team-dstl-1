# Extract

Code to extract telemetry and a frame from the provided logs and video footage. In reality, this would be replaced with a direct feed from the drone sensors on the on-board computer.

## Usage

The following arguments can be passed to the script:

| Short Option | Long Option | Description |
| ------------ | ----------- | ----------- |
| -e | --extracted | Root name of the output files to create. Optional, defaults to `extracted`. |
| -l | --logfile | Path to the telemetry log file |
| -o | --offset | The Unix timestamp (UTC) at which the video starts |
| -v | --video | Path to the video file (MP4 files are preferred). |
| -x | --extract | The Unix timestamp (UTC) at which to extract the frame and metadata |

## Example

```
python3 extract.py -v "/home/james/data/videos/sample8/sample8/logitech_08_47_29.avi" \
                   -o 1676450849 \
                   -l "/home/james/data/videos/sample8/logs/2023-02-15 10-35-41.tlog" \
                   -x 1676452324
```