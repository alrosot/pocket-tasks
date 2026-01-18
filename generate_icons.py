import torch
from diffusers import StableDiffusionPipeline

# Load the model
pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
pipe = pipe.to("mps")

# Prompts
prompts = [
    "A happy boy with a soccer ball, black and white, simple, high contrast, icon style",
    "A happy boy reading a book, black and white, simple, high contrast, icon style"
]
image_names = ["soccer_kid.png", "book_kid.png"]

# Generate and save images
for i, prompt in enumerate(prompts):
    image = pipe(prompt).images[0]
    image.save(image_names[i])
    print(f"Generated {image_names[i]}")
