import torch
import torchvision.transforms as transforms
from PIL import Image, ImageDraw
import numpy as np
from scipy.spatial import Voronoi
import random
import math

# --- Conversion Function ---
def tensor_to_pil(image_tensor):
    """
    Convert a tensor image to a PIL image.
    If the tensor is of shape (batch, height, width, channels) (i.e. channels in dim 1 > 4),
    it is permuted to (batch, channels, height, width) and the batch dimension is removed.
    """
    if image_tensor.dim() == 4:
        # If more than 4 channels in the second dimension, assume (batch, height, width, channels)
        if image_tensor.shape[1] > 4:
            image_tensor = image_tensor.permute(0, 3, 1, 2)
        image_tensor = image_tensor.squeeze(0)  # Remove the batch dimension
    transform = transforms.ToPILImage()
    return transform(image_tensor)

# --- Utility Functions ---
def get_brightness(x, y, img_array):
    """
    Calculate brightness using standard luminance weights.
    """
    h, w = img_array.shape[0], img_array.shape[1]
    xi = int(np.clip(x, 0, w - 1))
    yi = int(np.clip(y, 0, h - 1))
    r, g, b = img_array[yi, xi, :3]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def point_in_poly(x, y, poly):
    # Ray-casting algorithm for point-in-polygon test
    inside = False
    n = len(poly)
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if min(p1y, p2y) < y <= max(p1y, p2y):
            if p1y != p2y:
                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
            else:
                xinters = p1x
            if x <= xinters:
                inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite Voronoi regions in 2D to finite regions.
    Adapted from: https://stackoverflow.com/a/20678647/3357935
    """
    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")
    new_regions = []
    new_vertices = vor.vertices.tolist()
    
    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max() * 2

    # Map ridge vertices to all ridges for each point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))
    
    # Reconstruct each region
    for p_idx, region_idx in enumerate(vor.point_region):
        vertices = vor.regions[region_idx]
        if all(v >= 0 for v in vertices):
            new_regions.append(vertices)
            continue
        
        ridges = all_ridges[p_idx]
        new_region = [v for v in vertices if v >= 0]
        
        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                continue
            t = vor.points[p2] - vor.points[p_idx]
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])
            midpoint = vor.points[[p_idx, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius
            new_vertices.append(far_point.tolist())
            new_region.append(len(new_vertices) - 1)
        
        vs = np.array([new_vertices[v] for v in new_region])
        angles = np.arctan2(vs[:,1] - center[1], vs[:,0] - center[0])
        new_region = [v for _, v in sorted(zip(angles, new_region))]
        new_regions.append(new_region)
    
    return new_regions, np.array(new_vertices)

def compute_weighted_centroid(polygon, img_array, sample_count):
    """
    Compute a weighted centroid for a polygon via Monte Carlo sampling.
    """
    xs, ys = zip(*polygon)
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    sum_x, sum_y, sum_w = 0.0, 0.0, 0.0
    valid_samples = 0
    for _ in range(sample_count):
        rx = random.uniform(min_x, max_x)
        ry = random.uniform(min_y, max_y)
        if point_in_poly(rx, ry, polygon):
            brightness = get_brightness(rx, ry, img_array)
            weight = brightness / 255.0  # For white dots on a dark background
            sum_x += rx * weight
            sum_y += ry * weight
            sum_w += weight
            valid_samples += 1
    if sum_w == 0 or valid_samples == 0:
        return (sum(xs) / len(xs), sum(ys) / len(ys))
    return (sum_x / sum_w, sum_y / sum_w)

def generate_stipple_art(image_tensor, 
                         stipple_count=1000, 
                         iteration_count=100, 
                         sample_count=30, 
                         white_cutoff=0.5,
                         min_dot_size=1, 
                         dot_size_range=2,
                         dot_color=(255, 255, 255),
                         background_color=(51, 51, 51),
                         random_seed=42):
    """
    Generate stipple art from an input image tensor.
    Returns a PIL image.
    """
    # Convert the tensor to a PIL image (the conversion function corrects the dimensions)
    pil_image = tensor_to_pil(image_tensor)
    width, height = pil_image.size
    img_array = np.array(pil_image).astype(np.float32)
    
    random.seed(random_seed)
    
    # Generate initial stipple points weighted by brightness.
    points = []
    while len(points) < stipple_count:
        x = random.uniform(0, width)
        y = random.uniform(0, height)
        brightness = get_brightness(x, y, img_array)
        weight = brightness / 255.0
        if weight > white_cutoff and random.random() < weight:
            points.append((x, y))
    while len(points) < stipple_count:
        points.append((random.uniform(0, width), random.uniform(0, height)))
    
    # Refine points iteratively using weighted Voronoi centroids.
    for _ in range(iteration_count):
        pts = np.array(points)
        vor = Voronoi(pts)
        regions, vertices = voronoi_finite_polygons_2d(vor, radius=width+height)
        new_points = []
        for region in regions:
            poly = vertices[region]
            poly[:,0] = np.clip(poly[:,0], 0, width)
            poly[:,1] = np.clip(poly[:,1], 0, height)
            centroid = compute_weighted_centroid(poly.tolist(), img_array, sample_count)
            new_points.append(centroid)
        points = new_points
    
    # Create a new image with a dark background.
    stipple_img = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(stipple_img)
    
    # Draw dots with radius based on local brightness.
    for (x, y) in points:
        brightness = get_brightness(x, y, img_array)
        norm = brightness / 255.0  # Normalize brightness
        dot_radius = min_dot_size + norm * dot_size_range
        bbox = [x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius]
        draw.ellipse(bbox, fill=dot_color)
    
    return stipple_img

# --- Main Code Execution ---
# The input image is provided as a tensor via the custom node input (variable name: image).
if image is None:
    raise ValueError("No image tensor provided")

# Generate the stipple art as a PIL image.
stipple_art = generate_stipple_art(
    image, 
    stipple_count=1000, 
    iteration_count=100, 
    sample_count=30, 
    white_cutoff=0.5,
    min_dot_size=1, 
    dot_size_range=2,
    dot_color=(255, 255, 255),
    background_color=(51, 51, 51),
    random_seed=42
)

# Convert the PIL image back to a tensor so that the output format matches the input.
to_tensor = transforms.ToTensor()
output_tensor = to_tensor(stipple_art)

# Set the required global outputs.
output = "Stipple art generated successfully."
image = output_tensor  # The image is now output as a tensor.
