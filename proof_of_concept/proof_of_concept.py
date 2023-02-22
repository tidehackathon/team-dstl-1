import argparse
import sys
import time

sys.path.append('../extract')
import extract

# TODO: Speed up extraction by not re-reading entire log file every time - extract useful bits into memory initially?

def get_start_location(log, timestamp):
    m = extract.extract_metadata(log, timestamp)

    return logfile_coord_to_dec(m["_lat"]), logfile_coord_to_dec(m["_lon"])

def logfile_coord_to_dec(coord):
    return coord / 10000000

if __name__=="__main__":
    a = argparse.ArgumentParser(
        prog = 'Proof of Concept',
        description = 'Performs a real time proof of concept demonstration of the technique'
    )

    a.add_argument("logfile", help="Path to telemetry log file")
    a.add_argument("video", help="Path to video file")
    a.add_argument("offset", help="Unix timestamp (in UTC) of the start of the video", type=float)

    args = a.parse_args()


    # Extract first frame and geolocation, assuming this is where we lose GPS
    start_lat, start_lon = get_start_location(args.logfile, args.offset)

    print(f"Start location: {start_lat}, {start_lon}")

    start_time = time.time()

    ground_truth = []
    predicted = []

    while True:
        # Get latest data, using real time offset from when we started
        offset = time.time() - start_time
        print(f"Time offset: {offset}")

        # Get sensor data
        drone_metadata = extract.extract_metadata(args.logfile, args.offset + offset)
        if drone_metadata is None:
            print("Ran out of log data")
            break

        # Get video data
        image = extract.extract_frame(args.video, offset)
        if image is None:
            print("Ran out of video data")
            break

        # Save ground truth location
        ground_truth.append((logfile_coord_to_dec(drone_metadata["_lat"]), logfile_coord_to_dec(drone_metadata["_lon"])))
        
        # TODO: Get mapping

        # TODO: Get location via neural network

        # TODO: Calculate offset

        # TODO: Save offset location into predicted
    
    # TODO: Create plot/image showing difference between ground truth and predicted - KML?