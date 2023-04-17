from PIL import Image

def resize_image(img, max_size):
    width, height = img.size
    ratio = min(max_size / width, max_size / height)
    new_width = int(width * ratio)
    new_height = int(height * ratio)
    return img.resize((new_width, new_height), Image.ANTIALIAS)

def process_image(file):
    img = Image.open(file.stream)
    img = resize_image(img, 800)  # Ajustar el tamaño máximo según sea necesario

    # Continúa con el procesamiento como antes
