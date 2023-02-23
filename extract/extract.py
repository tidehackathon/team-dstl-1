from pymavlink import mavutil
import cv2
import argparse
import json

def extract_metadata(log, extract):
    mlog = mavutil.mavlink_connection(log)

    extract_dict = {}

    while True:
        try:
            m = mlog.recv_match(type=['VFR_HUD', 'ATTITUDE', 'MOUNT_STATUS', 'AHRS3', 'AHRS2', 'GLOBAL_POSITION_INT'])
            if m is None:
                break

            timestamp = getattr(m, '_timestamp', 0.0)
            if timestamp > extract:
                break

            extract_dict['timestamp'] = timestamp

            if isinstance(m, mavutil.mavlink.MAVLink_vfr_hud_message):
                extract_dict['heading'] = m.heading
                extract_dict['altitude'] = m.alt
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
            elif isinstance(m, mavutil.mavlink.MAVLink_global_position_int_message):
                extract_dict['_lat'] = m.lat
                extract_dict['_lon'] = m.lon
            else:
                print(f"WARNING: Unexpected type {type(m)}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return None
    
    return extract_dict
        

def extract_frame(input_video, offset):
    try:
        video = cv2.VideoCapture(input_video)
        video.set(cv2.CAP_PROP_POS_MSEC, offset*1000)
        _, image = video.read()
        return image
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None


def save_frame(input_video, video_offset, extract, output_image):
    try:
        image = extract_frame(input_video, extract-video_offset)
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

    save_frame(args.video, args.offset, args.extract, args.extracted + ".jpg")
    