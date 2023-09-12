#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2023 Aleksandra Badaczewska 
#
# GNU GENERAL PUBLIC LICENSE, version 3.0

"""
    Automated selector for representative GCP images, minimizing manual inspection.
"""

import csv
import sys
from collections import defaultdict
from operator import itemgetter
import argparse


def calculate_distance(x, y, center_x, center_y):
    """
    Calculate the Euclidean distance from the center of the image.
        Parameters: x, y (coordinates of the point); center_x, center_y (coordinates of the image center)
        Returns float: Euclidean distance
    """
    return ((x - center_x)**2 + (y - center_y)**2)**0.5


def main(args):
    # Constants for image dimensions and center
    DATA_FILE = args.data_file_path
    IMAGE_WIDTH = args.image_width
    IMAGE_HEIGHT = args.image_height
    N_IMAGES = args.images_number
    CENTER_X = IMAGE_WIDTH // 2
    CENTER_Y = IMAGE_HEIGHT // 2

    # Load data from file
    data = []
    ix = 3           # index of x coordinate in 7-col file
    iy = 4           # index of y coordinate in 7-col file
    im = 6           # index of ArUco marker ID in 7-col file
    with open(DATA_FILE, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            # Process only 4 or 7-column lines
            if len(row) != 4 and len(row) != 7:
                continue
            if len(row) == 4:
                ix = 0
                iy = 1
                im = 3
            # Calculate the distance from the center for each marker
            x = int(row[ix])
            y = int(row[iy])
            distance = calculate_distance(x, y, CENTER_X, CENTER_Y)
            data.append(row + [distance])

    # Group data by marker ID
    grouped_data = defaultdict(list)
    for row in data:
        marker_id = row[im]
        grouped_data[marker_id].append(row)

    # Select the top N images for each marker ID based on the distance
    selected_data = []
    for marker_id, rows in grouped_data.items():
        sorted_rows = sorted(rows, key=itemgetter(-1))
        selected_data.extend(sorted_rows[:N_IMAGES])

    # Save the selected data to the specified output file
    with open(args.output, 'w') as outfile:
        for row in selected_data:
            outfile.write(' '.join(row[:-1]) + '\n')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated selector for representative images with GCP markers.",
                                     epilog="Example: python gcp_images_picker.py -i <data_file> -w <image_width> -h <image_height> -n <images_number>")
    
    parser.add_argument('-i', '--data-file-path', type=str, required=True, help="path to the data file")
    parser.add_argument('-w', '--image-width', type=int, required=True, help="width of the image")
    parser.add_argument('-l', '--image-height', type=int, required=True, help="height of the image")
    parser.add_argument('-n', '--images-number', type=int, default=10, help="number of images to select")
    parser.add_argument('-o', '--output', type=str, default="gcp_list_selected.txt", help="name of the output file")
    
    args = parser.parse_args()
    main(args)
