# 🚀 anyPython

A custom node for ComfyUI where you can paste/type any python code and it will get executed when you run the workflow.

## Why this node?
-----------
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


This node was inspired by [AnyNode](https://github.com/lks-ai/anynode).
You can use this node in combination with a Custom node like the [Ollama node](https://github.com/stavsap/comfyui-ollama) that can generate the python code and feed into this node.

Let me know in the discussion how you would use this node.

## Instruction for usage
-----------
- The string variable will be passed as a local variable called "variable". You can directly used "variable" in your code and it should work. In case what you are passing is an int or float, you might have to declare the variable as int or float to make it work.
- Images are passed as a tensor image object in ComfyUI. You will need to write your own python code to convert that image into what you need in order to use it in your python code. Refer examples in the workflow folder on how the image node has been used.

Here's an example of a python script that I used in order to take a single image as input and convert it to pil image.

```python
import torch
import torchvision.transforms as transforms
from PIL import Image

# Assuming 'image' is your tensor image object with incorrect dimensions
# Correcting the dimensions if they are in (batch size, height, width, channels) format
if image.shape[1] > 4:  # More than 4 channels suggests incorrect dimension order
    image = image.permute(0, 3, 1, 2)  # Rearrange to (batch size, channels, height, width)

# Continue with conversion and saving as before
image = image.squeeze(0)  # Remove the batch dimension
transform = transforms.ToPILImage()
pil_image = transform(image)

```

![ComfyUI anyPython example workflow](/resources/img/comfyUI-anyPython-example-workflow.png)


## IMPORTANT! Security
As you might be already thinking, since this can run any python code, it can run malicious codes also. You need to be extremely careful what code is being put in the node. It's also possible that someone might share a complex workflow with this node with malicious scripts already populated in the anyPython node. If you have acquired the comfyUI workflow from someone else you need to be vigilant and review any workflow that involves any anyPython node. Review each anyPython nodes individually. If you don't understand the code, copy it and let a LLM like Copilot or GPT review the code.

