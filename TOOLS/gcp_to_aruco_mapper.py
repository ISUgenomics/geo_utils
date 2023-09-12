#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
    Maps custom GCP IDs to corresponding ArUco marker IDs in imagery (uses WGS84 datum).
"""

import os
import argparse
from math import sin, cos, sqrt, atan2, radians
from PIL import Image
from pyproj import Proj, transform


def transform_to_wgs84(x, y, zone):
    """
    Transforms coordinates from given UTM zone (WGS84 datum) to WGS84 latitude and longitude.
    """
    in_proj = Proj(proj='utm', zone=zone, datum='WGS84')
    out_proj = Proj(proj='latlong', datum='WGS84')
    lon, lat = transform(in_proj, out_proj, x, y)
    return lat, lon


def extract_gps_from_exif(image_path):
    """
    Extract GPS coordinates and altitude from an image's EXIF data.
        Returns tuple: (longitude, latitude, altitude) if GPS data is found.
        Note: The function assumes the GPS EXIF data is in the format of degrees, minutes, and seconds (DMS).
    """
    image = Image.open(image_path)
    exif_data = image._getexif()
    
    # The value 34853 corresponds to the EXIF tag ID for GPS information in images. 
    if not exif_data or 34853 not in exif_data:
        return None
    gps_info = exif_data[34853]
    
    latitude_dms = gps_info[2]
    latitude = float(latitude_dms[0]) + float(latitude_dms[1])/60 + float(latitude_dms[2])/3600
    if gps_info[1] == 'S':
        latitude = -latitude
    longitude_dms = gps_info[4]
    longitude = float(longitude_dms[0]) + float(longitude_dms[1])/60 + float(longitude_dms[2])/3600
    if gps_info[3] == 'W':
        longitude = -longitude
    altitude = float(gps_info[6])
    return longitude, latitude, altitude


def calculate_distance(coord1, coord2):
    """
    Calculate the great-circle distance between two GPS coordinates on the Earth's surface using the Haversine formula.
        Parameters: coord1, coord2 are tuples; The format for each should be (latitude, longitude).
        Returns float: The distance between the two points in meters.
        Note: The function assumes that the Earth is a perfect sphere, which might introduce 
              small errors in the calculated distance, especially for very long distances.
    """
    lat1, lon1 = coord1[:2]
    lat2, lon2 = coord2[:2]

    R = 6371000            # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c       # in meters
    return distance


def load_gcps(filename, zone):
    """
    Load Ground Control Points (GCPs) from a file and transform their coordinates to WGS 84.
        Parameters: filename (space separated 4-columns: gcp_id x y z); zone (The UTM zone in which the GCP coordinates.)
        Returns dict: A dictionary with GCP IDs as keys and their corresponding (longitude, latitude)
        Note: The function assumes the provided UTM coordinates use the WGS 84 datum.
    """
    with open(filename, 'r') as file:
        lines = file.readlines()
        gcps = {}
        for line in lines:
            data = line.strip().split(' ')
            label = int(data[0])
            x, y = float(data[1]), float(data[2])
            lat, lon = transform_to_wgs84(x, y, zone)
            gcps[label] = (lon, lat)    # store as (longitude, latitude) for consistency
    return gcps


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Maps custom GCP IDs to corresponding ArUco marker IDs in imagery (uses WGS84 datum).",
        epilog="Example:\n        python gcp_to_aruco_mapper.py -g <gcp_file> -i <imagery_dir> -z 11 -o <output_file> -d 50"
    )
    parser.add_argument('-g', '--gcp-file', type=str, required=True, help='Path to the GCP file')
    parser.add_argument('-i','--imagery-path', type=str, required=True, help='Path to the imagery')
    parser.add_argument('-z', '--zone', type=int, required=True, help='UTM Zone')
    parser.add_argument('-o','--output', type=str, default="gcp_to_image_matches.txt", help='Path to the output file')
    parser.add_argument('-d', '--max_dist', type=int, default=100, help='Distance threshold in meters')
    
    args = parser.parse_args()

    # Make sure the GCP file exists
    if not os.path.exists(args.gcp_file):
        print(f"Error: {args.gcp_file} does not exist!")
        exit(1)

    # Load the Ground Control Points
    gcps = load_gcps(args.gcp_file, args.zone)

    # Set distance threshold
    MAX_DISTANCE = args.max_dist  # meters
    all_distances = []

    # Process the imagery
    image_extensions = ['.jpg', '.jpeg', '.tiff', '.tif', '.dng', '.png', '.webp']  # several image formats that contain EXIF data
    for filename in os.listdir(args.imagery_path):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_gps = extract_gps_from_exif(os.path.join(args.imagery_path, filename))
    
            if not image_gps:
                continue  # Skip this iteration if GPS data is not found for the image

            for gcp_id, gcp_coords in gcps.items():
                distance = calculate_distance(image_gps, gcp_coords)
                print(f"Distance from {filename} to GCP {gcp_id}: {distance:.2f} meters.")
                all_distances.append((gcp_id, filename, distance))

    # Sort by distance
    all_distances.sort(key=lambda x: x[2])

    best_matches = {}
    used_images = set()
    used_gcp = set()
    potential_matches = {}  # Store potential matches for images

    # Find best matches
    for gcp_id, filename, distance in all_distances:
        if distance <= MAX_DISTANCE:
            # Store potential matches for this image
            if filename not in potential_matches:
                potential_matches[filename] = (gcp_id, distance)
        
            # If GCP and image are not used, store the match
            if gcp_id not in used_gcp and filename not in used_images:
                best_matches[gcp_id] = (filename, distance)
                used_images.add(filename)
                used_gcp.add(gcp_id)

    # Print matches and check for better potential matches
    for gcp_id, (closest_image, closest_distance) in best_matches.items():
        marker_id = closest_image.split("_")[-1].split(".")[0]
        with open(args.output, "a") as file:
            file.write(f"Match found: GCP {gcp_id} (d={closest_distance:.2f}m) is likely in image {closest_image} with ArUco marker {marker_id}.\n")

        potential_gcp, potential_distance = potential_matches.get(closest_image, (None, None))
        if potential_gcp and potential_gcp != gcp_id and potential_distance < closest_distance:
            with open(args.output, "a") as file:
                file.write(f"       Note: GCP {potential_gcp} (d={potential_distance:.2f}m) had a closer distance for image {closest_image} but was matched with another image.\n")
    
    # Print unmatched GCPs
    unmatched_gcps = set(gcps.keys()) - used_gcp
    for gcp_id in unmatched_gcps:
        with open(args.output, "a") as file:
            file.write(f"       Note: GCP {gcp_id} - No match found!\n")