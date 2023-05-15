from concurrent.futures import ThreadPoolExecutor
from utils.qr import *
from utils.config import cfg
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

def rotate_image(path, angle, measure_current, measure_w, measure_h):
    img_canvas = False
    path_canvas = ""
    
    try:
        angle = int(angle) - 90
        img = Image.open(path)
        img = img.rotate(angle, expand=True)
        if abs(angle) < 360:
            filename = str(path.split("/")[-1]).split(".")[0] + '_rot'+ str(abs(angle)) + '.jpg'
            path = cfg.GLOBAL.QR_IMAGES + '/' + filename
            img.save(path)
        else:
            filename = str(path.split("/")[-1]).split(".")[0] + '.jpg'
            angle = 0
        path_canvas = cfg.GLOBAL.QR_IMAGES_WEB + '/' + filename
        measure_w = int(str(measure_w).split("px")[0])
        measure_h = int(str(measure_h).split("px")[0])

        if measure_current=='H':
            measure = "W"
            if measure_w > measure_h:
                measure_width = measure_w
                measure_height = measure_h
            else:
                measure_width = measure_h
                measure_height = measure_w
        else:
            measure = 'H'
            if measure_w > measure_h:
                measure_width = measure_h
                measure_height = measure_w
            else:
                measure_width = measure_w
                measure_height = measure_h

        img_canvas = True
    except Exception as e:
            print(e)
            print("Error generate text...")
    
    return img_canvas, path_canvas, angle, measure, measure_width, measure_height


# def process_images(files):
#     results = []
#     with ThreadPoolExecutor() as executor:
#         futures = []
#         for file in files:
#             futures.append(executor.submit(process_image, file))
#         for future in concurrent.futures.as_completed(futures):
#             results.append(future.result())
#     return results

def process_images(files):
    results = []
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_image, files))
    return results

def process_image(file, list_bill):
    measure = []

    # Guardar el archivo correspondiente IMG o PDF
    img, path = save_file(file)
    # Obtener medidas de la Imagen
    measure = parse_img_data(img)
    # Procesar el código QR
    data, bill = parse_qr_data(img, measure, path, list_bill)

    # Data OK y Bill No es Repetido
    if len(data)>0:
        return data, bill
    # # Data NULL y Bill es Repetido
    else:
        # Extraer texto de la imagen
        text = pytesseract.image_to_string(img, lang='spa', config='--dpi 2 --psm 6')
        data, bill = parse_text_data(text, measure, path, list_bill)
        # Buscar datos en el texto
        return data, bill