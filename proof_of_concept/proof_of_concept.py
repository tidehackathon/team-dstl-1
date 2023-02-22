import argparse
import json
import sys
import time

sys.path.append('../extract')
import extract

sys.path.append('../download')
import tiles_to_tiff as t3

def get_start_location(log, timestamp):
    m = extract.extract_metadata(log, timestamp)

    return logfile_coord_to_dec(m["_lat"]), logfile_coord_to_dec(m["_lon"])

def logfile_coord_to_dec(coord):
    return coord / 10000000

if __name__=="__main__":
    with open("config.json") as f:
        config = json.load(f)

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

    ground_truth = [(start_lon, start_lat)]
    predicted = [(start_lon, start_lat)]
    time_offsets = [0]

    # Create empty output CSV
    with open("output.csv", "w") as f:
        f.write("offset,predicted_lon,predicted_lat,truth_lon,truth_lat\n")
        f.write(f"{time_offsets[0]},{predicted[0][0]},{predicted[0][1]},{ground_truth[0][0]},{ground_truth[0][1]}\n")


    while True:
        # Get latest data, using real time offset from when we started
        offset = time.time() - start_time
        time_offsets.append(offset)
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
        
        # Get mapping
        bounds = [
            predicted[-1][0] - (config["width"] / 2),
            predicted[-1][1] - (config["height"] / 2),
            predicted[-1][0] + (config["width"] / 2),
            predicted[-1][1] + (config["height"] / 2)
        ]
        t3.convert(config["url"], "./merged.tif", bounds, config["zoom"])

        # TODO: Rectify the images

        # TODO: Get location via neural network
        nn_location = (0, 0)

        # TODO: Calculate offset to drone location
        corrected_location = (0, 0)

        # Save offset location into predicted
        predicted.append(corrected_location)

        # Save ground truth/prediction to CSV
        with open("output.csv", "a") as f:
            f.write(f"{offset},{predicted[-1][0]},{predicted[-1][1]},{ground_truth[-1][0]},{ground_truth[-1][1]}\n")

    # TODO: Create plot/image showing difference between ground truth and predicted