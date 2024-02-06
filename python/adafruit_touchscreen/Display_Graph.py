
def display_image():
    image = Image.open("graph.bmp").convert("RGB")

    # Scale the BMP image to fit the screen
    image = image.resize((width, height), Image.BICUBIC)

    # Display the BMP image on the touchscreen
    disp.image(image)

