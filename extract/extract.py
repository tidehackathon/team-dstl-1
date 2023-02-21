from pymavlink import mavutil
import cv2
import argparse
import json

def extract_metadata(log, extract):
    mlog = mavutil.mavlink_connection(log)

    extract_dict = {}

    while True:
        try:
            m = mlog.recv_match(type=['NAV_CONTROLLER_OUTPUT', 'ATTITUDE', 'MOUNT_STATUS', 'AHRS3', 'AHRS2'])
            if m is None:
                break

            timestamp = getattr(m, '_timestamp', 0.0)
            if timestamp > extract:
                break

            if isinstance(m, mavutil.mavlink.MAVLink_nav_controller_output_message):
                extract_dict['nav_bearing'] = m.nav_bearing
            elif isinstance(m, mavutil.mavlink.MAVLink_attitude_message):
                extract_dict['yaw'] = m.yaw
                extract_dict['pitch'] = m.pitch
                extract_dict['roll'] = m.roll
            elif isinstance(m, mavutil.mavlink.MAVLink_mount_status_message):
                extract_dict['camera_a'] = m.pointing_a     #    input_a : pitch(deg*100) or lat, depending on mount mode (int32_t)
                extract_dict['camera_b'] = m.pointing_b     #    input_b : roll(deg*100) or lon depending on mount mode (int32_t)
                extract_dict['camera_c'] = m.pointing_c     #    input_c : yaw(deg*100) or alt (in cm) depending on mount mode (int32_t)
            elif isinstance(m, mavutil.mavlink.MAVLink_ahrs3_message) or isinstance(m, mavutil.mavlink.MAVLink_ahrs2_message):
                extract_dict['altitude'] = m.altitude
            else:
                print(f"WARNING: Unexpected type {type(m)}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            break
    
    return extract_dict
        

def extract_frame(input_video, video_offset, extract, output_image):
    try:
        video = cv2.VideoCapture(input_video)
        video.set(cv2.CAP_PROP_POS_MSEC, (extract-video_offset)*1000)
        _, image = video.read()
        cv2.imwrite(output_image, image)
    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__=="__main__":
    a = argparse.ArgumentParser(
        prog = 'Extract Drone Instant',
        description = 'Extracts video and metadata for an instant in time from a drone flight'
    )

    a.add_argument("-v", "--video", help="Path to video file", required=True)
    a.add_argument("-o", "--offset", help="Unix timestamp (in UTC) of the start of the video", type=float, required=True)

    a.add_argument("-l", "--logfile", help="Path to telemetry log file", required=True)

    a.add_argument("-x", "--extract", help="Unix timestamp (in UTC) of the extraction instant", type=float, required=True)

    a.add_argument("-e", "--extracted", help="Root name of output files", default="extracted")

    args = a.parse_args()

    metadata = extract_metadata(args.logfile, args.extract)
    with open(args.extracted + ".json", 'w') as f:
        json.dump(metadata, f)

    extract_frame(args.video, args.offset, args.extract, args.extracted + ".jpg")
    