import csv
import sys
from collections import defaultdict
from operator import itemgetter

if len(sys.argv) != 5:
    print("Usage: python gcp_images_picker.py <data_file_path> <image_width> <image_height> <images_number>")
    sys.exit(1)

# Constants for image dimensions and center
DATA_FILE = sys.argv[1]
IMAGE_WIDTH = int(sys.argv[2])
IMAGE_HEIGHT = int(sys.argv[3])
N_IMAGES = int(sys.argv[4])
CENTER_X = IMAGE_WIDTH // 2
CENTER_Y = IMAGE_HEIGHT // 2

def calculate_distance(x, y):
    """Calculate the Euclidean distance from the center of the image."""
    return ((x - CENTER_X)**2 + (y - CENTER_Y)**2)**0.5

# Load data from file
data = []
with open(DATA_FILE, 'r') as f:
    # Skip the EPSG line
    next(f)
    
    # Read the rest of the data
    reader = csv.reader(f, delimiter=' ')
    for row in reader:
        # Calculate the distance from the center for each marker
        distance = calculate_distance(int(row[3]), int(row[4]))
        data.append(row + [distance])

# Group data by marker ID (7th column, index 6)
grouped_data = defaultdict(list)
for row in data:
    marker_id = row[6]
    grouped_data[marker_id].append(row)

# Select the top N images for each marker ID based on the distance
selected_data = []
for marker_id, rows in grouped_data.items():
    sorted_rows = sorted(rows, key=itemgetter(-1))
    selected_data.extend(sorted_rows[:N_IMAGES])

# Save the selected data to a new file or print it
for row in selected_data:
    print(' '.join(row[:-1]))
