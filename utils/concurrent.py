from concurrent.futures import ThreadPoolExecutor
from utils.qr import *
from PIL import Image
from utils.config import cfg
import concurrent.futures
import pytesseract
import cv2

pytesseract.pytesseract.tesseract_cmd = cfg.GLOBAL.GLOBAL_TESS


def getting_text(path, dictCanvas):
    # dictCanvas = json.loads(request.values.get("dictCanvas"))
    i = 0
    text_canvas = ""
    image = None
    # dictPage = None
    for dictVal in dictCanvas:
        i += 1
        # print("image path", image)
        image = cv2.imread(path, 0)
        # thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        _y = dictVal['y']
        _h = dictVal['h']
        _x = dictVal['x']
        _w = dictVal['w']
        # print("X Y W H", str(_x) + " " + str(_y) + " " + str(_w) + " " + str(_h))
        # ROI = thresh[dictVal['y']:dictVal['y']+dictVal['h'], dictVal['x']:dictVal['x']+dictVal['w']]
        ROI = image[_y: _y + _h, _x: _x + _w]
        # print("ROI", ROI)
        language = "spa"
        try:
            text_canvas = pytesseract.image_to_string(ROI, lang=language, config='--psm 6')
            # result_canvas = True
            print("TEXT FINAL,", text_canvas)
        except Exception as e:
                print(e)
                print("Error generate text...")
    
    return text_canvas

def process_images(files):
    # results = []
    with ThreadPoolExecutor() as executor:
        # results = list(executor.map(process_image, files))
        results = []
        for file in files:
            results.append(executor.submit(process_image, file))
        for future in concurrent.futures.as_completed(results):
            print(future.result())
    return results

def process_image(file):
    measure = []

    # Guardar el archivo correspondiente IMG o PDF
    img, path = save_file(file)
    
    # Obtener medidas de la Imagen
    measure = parse_img_data(img)

    # Procesar el código QR
    data = parse_qr_data(img, measure, path)

    if len(data)>0:
        return data
    else:
        # Extraer texto de la imagen
        text = pytesseract.image_to_string(img, lang='spa', config='--psm 6')

        # Buscar datos en el texto
        return parse_text_data(text, measure, path)
        