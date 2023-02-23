import argparse
import json
import numpy as np
import rasterio
import simplekml
import sys
import time

sys.path.append('../extract')
import extract

sys.path.append('../download')
import tiles_to_tiff as t3

sys.path.append('../mapping') 
import find_drone_coords as fdc

sys.path.append('../offset_correction')
import offset_correction

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
    raw_predicted = [(start_lon, start_lat)]
    predicted = [(start_lon, start_lat)]
    time_offsets = [0]

    # Create empty output CSV
    with open("output.csv", "w") as f:
        f.write("offset,predicted_lon,predicted_lat,truth_lon,truth_lat\n")
        f.write(f"{time_offsets[0]},{predicted[0][0]},{predicted[0][1]},{ground_truth[0][0]},{ground_truth[0][1]}\n")

    # Create empty KML
    kml = simplekml.Kml(name='Proof of Concept')
    gt_line = kml.newlinestring(name="Ground Truth", coords=ground_truth)
    gt_line.style.linestyle.color = simplekml.Color.limegreen
    gt_line.style.linestyle.width = 10

    raw_pred_line = kml.newlinestring(name="Predicted (Uncorrected)", coords=raw_predicted)
    raw_pred_line.style.linestyle.color = simplekml.Color.blue
    raw_pred_line.style.linestyle.width = 10 

    pred_line = kml.newlinestring(name="Predicted (Corrected)", coords=predicted)
    pred_line.style.linestyle.color = simplekml.Color.red
    pred_line.style.linestyle.width = 10

    kml.save("output.kml")

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
        ground_truth.append((logfile_coord_to_dec(drone_metadata["_lon"]), logfile_coord_to_dec(drone_metadata["_lat"])))
        
        # Get mapping
        bounds = [
            predicted[-1][0] - (config["width"] / 2),
            predicted[-1][1] - (config["height"] / 2),
            predicted[-1][0] + (config["width"] / 2),
            predicted[-1][1] + (config["height"] / 2)
        ]
        t3.convert(config["url"], "./merged.tif", bounds, config["zoom"])

        # TODO: Rectify the images

        # Get location via neural network
        patch_size = int(config.get("patch_size", 512))
        stride_size = int(config.get("stride_size", patch_size / 4))

        pred_lat, pred_lon = fdc.drone_image_to_coords(np.asarray(image), rasterio.open("./merged.tif"), patch_size=patch_size, stride_size=stride_size)
        raw_predicted.append((pred_lon, pred_lat))

        # Calculate offset to drone location - use heading not yaw for platform so it's relative to N
        corrected_lat, corrected_lon = offset_correction.correct_offset_rot(pred_lat, pred_lon, drone_metadata["heading"], drone_metadata["pitch"], drone_metadata["roll"], drone_metadata["altitude"], config["ground_altitude"], drone_metadata["camera_a"], drone_metadata["camera_b"], drone_metadata["camera_c"])

        # Save offset location into predicted
        predicted.append((corrected_lon, corrected_lat))

        # Save ground truth/prediction to CSV
        with open("output.csv", "a") as f:
            f.write(f"{offset},{predicted[-1][0]},{predicted[-1][1]},{ground_truth[-1][0]},{ground_truth[-1][1]}\n")
        
        # Save ground truth/prediction to KML
        gt_line.coords = ground_truth
        raw_pred_line.coords = raw_predicted
        pred_line.coords = predicted
        kml.save("output.kml")
