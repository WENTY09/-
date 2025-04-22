import os
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

def create_delivery_image():
    """Returns path to delivery image."""
    # Check for custom image first
    custom_image_path = "delivery_custom.jpg"
    
    # If custom image exists and has content, use it
    if os.path.exists(custom_image_path) and os.path.getsize(custom_image_path) > 0:
        logger.info(f"Using custom image: {custom_image_path}")
        return custom_image_path
    
    # Use fallback image if it exists
    fallback_image = "delivery.png"
    if os.path.exists(fallback_image) and os.path.getsize(fallback_image) > 0:
        logger.info(f"Using existing fallback image: {fallback_image}")
        return fallback_image
    
    logger.info("Generating new default image")
    
    # Create a new image with a white background
    width, height = 500, 300
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    
    # Get a drawing context
    draw = ImageDraw.Draw(image)
    
    # Draw packages
    draw.rectangle((50, 100, 150, 200), fill=(200, 150, 100), outline=(100, 50, 0), width=3)
    draw.rectangle((200, 120, 300, 220), fill=(150, 200, 100), outline=(50, 100, 0), width=3)
    draw.rectangle((350, 80, 450, 180), fill=(100, 150, 200), outline=(0, 50, 100), width=3)
    
    # Draw delivery truck
    draw.rectangle((50, 40, 200, 80), fill=(255, 0, 0), outline=(0, 0, 0), width=2)  # body
    draw.rectangle((20, 45, 50, 80), fill=(200, 0, 0), outline=(0, 0, 0), width=2)   # cabin
    draw.ellipse((30, 75, 50, 95), fill=(0, 0, 0))  # wheel 1
    draw.ellipse((150, 75, 170, 95), fill=(0, 0, 0))  # wheel 2
    
    # Add text
    try:
        # Try to get a font
        font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        # If font not found, use default
        font = ImageFont.load_default()
    
    draw.text((150, 250), "Доставка посылок", fill=(0, 0, 0), font=font)
    
    # Save the image
    image.save(fallback_image)
    
    return fallback_image