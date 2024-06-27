'''
This code will take an image as input and set it as your Windows wallaper.
Works on Windows 11. Haven't tested on Win 10.
'''


import torch
import torchvision.transforms as transforms
from PIL import Image
import ctypes
import os
import getpass

# Assuming 'image' is your tensor image object with incorrect dimensions
# Correcting the dimensions if they are in (batch size, height, width, channels) format
if image.shape[1] > 4:  # More than 4 channels suggests incorrect dimension order
    image = image.permute(0, 3, 1, 2)  # Rearrange to (batch size, channels, height, width)

# Continue with conversion and saving as before
image = image.squeeze(0)  # Remove the batch dimension
transform = transforms.ToPILImage()
pil_image = transform(image)

# Save the PIL image in the specified path with dynamic current user replacement
current_user = getpass.getuser()
image_path = f"C:\\Users\\{current_user}\\Pictures\\Wallpaper\\wallpaper.png"  # Changed .bmp to .png
os.makedirs(os.path.dirname(image_path), exist_ok=True)  # Create directory if it doesn't exist
pil_image.save(image_path, 'PNG')  # Specify PNG format

# Use ctypes to change the wallpaper on Windows 11
SPI_SETDESKWALLPAPER = 20
ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_path, 3)

print("Successfully changed wallpaper!")
