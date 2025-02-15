# 🚀 anyPython 0.0.3
A custom node for ComfyUI where you can paste/type any python code and it will get executed when you run the workflow.

## 0.0.3 changes
Updated for the node to work with the latest ComfyUI version as of 14th Feb 2025.
Avoided using exec and eval fucntion to meet security requirements of ComfyUI.
Introduced a toggle button that restricts risky code by default. Risk message is given. User have to explicitly turn it on to run risky code.


## Why this node?
ComfyUI has a lot of custom nodes but you will still have a special use case for which there's no custom nodes available. You don't need to know how to write python code yourself. Use a LLM to generate the code you need, paste it in the node and voila!! you have your custom node which does exactly what you need.

Here's some example use cases for which I've used this node.
- For a given API, I want to get the json data and get a specific value. eg. I want the current temperature of a place using the weather API.
- I want the current date, time, day etc.
- For a given image, I want to calculate the dominant color and calculate a foreground color with proper contrast that can be used as font color to overlay on the image.
- For a given RGB color, convert it into hex value.
- For a given url, return the html
- For a given html, return all the text content with markdown syntax.
- set a given image as the wallpaper of my Win 11 PC.
- Fetch the text content from a url, summarize the text using a LLM and put the summary in a powerpoint file.

Let me know in the discussion how you would use this node.

# TLDR: Writing Python Code for anyPython

## Key Points:
- **Execution Environment:**  
  Your code runs as a module with pre-defined globals:
  - `variable` (string, optional)
  - `image` (tensor)
  - `confirm_risks` (boolean)

- **Input & Output Handling:**  
  - **Input Image:** Provided as a tensor.  
    → Convert to a PIL image for processing if needed, then convert back to a tensor.
  - **Outputs:**  
    - Set global `output` (string) or use `print()` for text output.
    - Set global `image` (tensor) for the image output.

- **Allowed:**  
  Standard Python code (functions, loops, imports).  
  External libraries (note: risky modules require risk confirmation).

- **Not Allowed:**  
  Top-level `return` statements.  
  Modifying system/environment state outside allowed globals.

## Example Skeleton:
```python
# Convert tensor to PIL image (for processing)
pil_img = tensor_to_pil(image)

# Process the image (e.g., create stipple art)
processed_img = create_stipple_art(pil_img)

# Convert the processed image back to tensor
output_tensor = transforms.ToTensor()(processed_img)

# Define outputs
output = "Processing complete."
image = output_tensor
```


# Guide for Writing Python Code for anyPython

This guide explains how to write proper Python code to be used in a ComfyUI custom node. It covers how inputs and outputs are defined, what is allowed or not allowed, and provides example snippets.

---

## 1. Understanding the Node’s Execution Environment

- **Execution Context:**  
  Your code is written to a temporary file and executed using `runpy.run_path`. This means it runs as a module (i.e., top-level code) without the typical `if __name__ == '__main__':` guard.

- **Input Variables:**  
  The node creates a globals dictionary that includes:
  - `variable`: A string value (if provided).
  - `image`: An image input, always provided as a tensor.
  - `confirm_risks`: A boolean indicating whether you accept potential security risks.

- **Risk Confirmation:**  
  The node scans your code for risky operations (e.g., use of `os`, `sys`, or `subprocess`). If risky code is detected and `confirm_risks` is not set to `True`, execution is halted with a warning.

---

## 2. Defining the Outputs

The node expects **two outputs**:

- **String Output:**
  - The global variable `output` should hold the string output.
  - Alternatively, if `output` is not set, any text printed using `print()` is captured as the output.

- **Image Output:**
  - The global variable `image` should contain the image output.
  - **Important:** Since the input image is provided as a tensor, if you process the image as a PIL image, you must convert it back to a tensor before assigning it to `image`.

---

## 3. What Is Allowed and What Is Not

### Allowed:
- **Standard Python Code:**  
  You can write any valid Python code, define functions, use loops, etc.
- **Setting Globals for Output:**  
  Assign your final outputs to the global variables `output` and `image`.
- **Printing to Standard Output:**  
  Using `print("message")` is acceptable; the printed text will be captured if `output` is not defined.
- **Using External Libraries:**  
  Libraries such as `torch`, `numpy`, `PIL`, etc., can be imported.  
  *Caution:* Some modules (like `os`, `sys`, `subprocess`) are flagged as risky and require risk confirmation.

### Not Allowed / Cautions:
- **Top-Level `return` Statements:**  
  Do not use a top-level `return` statement in your code. Instead, assign the outputs to the globals.
- **Modifying the Node’s Environment:**  
  Avoid interfering with the provided globals (other than `output` and `image`) or modifying system-level settings without confirming risks.
- **Ignoring the Input Format:**  
  The input `image` is always a tensor. Convert it to a PIL image for processing if needed, then convert it back to a tensor before setting the output.

---

## 4. Suggested Code Structure

Below is a sample structure for your code:

```python
# --- Import necessary libraries ---
import torch
import torchvision.transforms as transforms
from PIL import Image, ImageDraw
import numpy as np
import random

# --- Helper Function to Convert Tensor to PIL Image ---
def tensor_to_pil(image_tensor):
    """
    Convert an image tensor to a PIL image.
    If the tensor is in (batch, height, width, channels) format,
    it will be permuted to (batch, channels, height, width) and squeezed.
    """
    if image_tensor.dim() == 4:
        if image_tensor.shape[1] > 4:  # Likely (batch, height, width, channels)
            image_tensor = image_tensor.permute(0, 3, 1, 2)
        image_tensor = image_tensor.squeeze(0)
    return transforms.ToPILImage()(image_tensor)

# --- Example Processing Function (e.g., creating stipple art) ---
def create_stipple_art(pil_img):
    width, height = pil_img.size
    # Create a new image with a dark background
    stipple_img = Image.new("RGB", (width, height), (51, 51, 51))
    draw = ImageDraw.Draw(stipple_img)
    
    # Example: Draw random white dots on the image
    for _ in range(500):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        dot_radius = random.randint(1, 3)
        draw.ellipse([x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius], fill=(255, 255, 255))
    
    return stipple_img

# --- Main Code Execution ---
# The input variables 'variable' and 'image' are provided automatically.
# 'image' is a tensor. Convert it to a PIL image for processing.
if image is None:
    raise ValueError("No image tensor provided")

# Convert tensor to PIL image for processing.
pil_img = tensor_to_pil(image)

# Process the image (for example, create stipple art)
processed_img = create_stipple_art(pil_img)

# Convert the processed PIL image back to a tensor.
to_tensor = transforms.ToTensor()
output_tensor = to_tensor(processed_img)

# --- Define Global Outputs ---
# For textual output:
output = "Stipple art created successfully."

# For image output (as a tensor to match the input format):
image = output_tensor

# Note:
# Do not use a 'return' statement in this code.
```

---

## 5. Key Points Recap

- **Input Variables:**
  - `variable` (string) – optional.
  - `image` (tensor) - (Optional) – the image input (must be converted if processing as a PIL image).
  - `confirm_risks` (boolean) – This is off by default. The code will not run if risk is detected. Check the string output for risk message. Toggle this on if you still want to run the script.

- **Output Variables:**
  - `output` (string) – if not defined, printed output is captured.
  - `image` (tensor) – must match the format of the input image.

- **Allowed Code:**
  - Standard Python code, function definitions, imports (with caution for risky modules), and assignment to globals.
  - **Avoid:** Top-level return statements or modifying system state without proper risk confirmation.

---

By following this structure and these guidelines, you can ensure that your Python code will execute properly within the ComfyUI custom node environment with the correct handling of both string and image outputs.


![ComfyUI anyPython example workflow](/resources/img/comfyUI-anyPython-example-workflow.png)


## IMPORTANT! Security
As you might be already thinking, since this can run any python code, it can run malicious codes also. You need to be extremely careful what code is being put in the node. It's also possible that someone might share a complex workflow with this node with malicious scripts already populated in the anyPython node. If you have acquired the comfyUI workflow from someone else you need to be vigilant and review any workflow that involves any anyPython node. Review each anyPython nodes individually. If you don't understand the code, copy it and let a LLM like Copilot or GPT review the code.