from PIL import Image
from pyzbar import pyzbar
from utils.config import cfg
import re
import os


def save_file(file):
    img = Image.open(file.stream)
    img_original = img
    filename = file.filename
    filename = filename.replace('(','').replace(')','').replace(',','').replace('<','').replace('>','').replace('?','').replace('!','').replace('@','').replace('%','').replace('$','').replace('#','').replace('*','').replace('&','').replace(';','').replace('{','').replace('}','').replace('[','').replace(']','').replace('|','').replace('=','').replace('+','').replace(' ','_')
    # Verify Image Name and Extension
    file_ext = filename.split(".")[-1]
    path = ""

    if (file_ext.upper()=='JPG' or  file_ext.upper()=='JPEG'):
        image_width  = 0
        image_height = 0

        if int(img.width)>int(img.height):
            image_height = 500
            image_width = 740
        else:
            file_width  = img.width
            file_height = img.height
            fw = float(int(file_height) / int(file_width))
            if fw > 2.0:
                image_width = 420
                image_height = 900
            elif fw > 1.75:
                image_width = 480
                image_height = 900
            else:
                image_width = 640
                image_height = 900
        # SAVE and ready to read by QR
        path = os.path.join(cfg.GLOBAL.GLOBAL_PATH + '/files/upload', filename)
        img = img.resize((image_width, image_height), Image.ANTIALIAS)
        img.save(path)
        path = os.path.join('files/upload', filename)
    elif (file_ext.upper()=='PDF'):
        # Extract IMG, SAVE IMG and ready to read by QR
        print("SAVE PDF")
   
    return img_original, path


def parse_img_data(img):
    measure = []
    
    if int(img.width)>int(img.height):
        measure = "W"
        measure_h = "500px"
        measure_w = "740px"
        center_w = "0px"
    else:
        fw = float(int(img.height) / int(img.width))
        if fw > 2.0:
            measure_w = "420px"
            measure_h = "900px"
            center_w = "160px"
        elif fw > 1.75:
            measure_w = "480px"
            measure_h = "900px"
            center_w = "130px"
        else:
            measure_w = "640px"
            measure_h = "900px"
            center_w = "50px"
    
    measure = {
                'measure':   measure,
                'measure_h': measure_h,
                'measure_w': measure_w,
                'center_w':  center_w
            }

    return measure


def get_barcodes(barcodeData):
    data = {}
    band_ciaruc = False
    band_clifac = False
    band_clitot = False
    data['type_doc'] = ""
    data['currency'] = "S"

    if len(barcodeData) > 7:
        data['is_full'] = 1
    for code in barcodeData:
        # Find RUC (cia and cli)
        if len(code)==11:
            if band_ciaruc==False:
                data['cia_ruc'] = code
                band_ciaruc = True
            else:
                data['cli_ruc'] = code
        # Find BILL
        if band_clifac==False:
            if len(code)>0 and (code[0]=='F' or code[0]=='B'):
                if code[0]=='F':
                    data['type_doc'] = "F"
                if code[0]=='B':
                    data['type_doc'] = "B"
                data['cli_fac'] = code[1:]
                band_clifac = True
            if len(code)>10 and str(code).count('-')==2:
                data['type_doc'] = "F"
                data['cli_fac'] = code
        else:
            data['cli_fac'] += '-' + code
            band_clifac = False
        # Find TOTAL and IGV
        if str(code).count('.') == 1 and len(code.rsplit('.')[-1]) == 2:
            if band_clitot==False:
                data['cli_igv'] = code
                data['cli_tot'] = code
                band_clitot = True
            else:
                data['cli_tot'] = code
        # Find DATE
        if len(code)==10 and (str(code).count('-')==2 or str(code).count('/')==2):
            data['cli_dat'] = code

    return data


def parse_qr_data(img, measure, path):
    print("processing qr ...")
    # Aquí va la lógica para extraer los datos del código QR
    data = []
    barcodes = pyzbar.decode(img)
        
    if len(barcodes) > 0 :
        # loop over the detected barcodes
        for barcode in barcodes:
            barcodeText = str(barcode.data.decode("utf-8"))
            barcodeData = barcodeText.split('|')
        # print("\nbarcodeData LEN", len(barcodeData))
        # print("barcodeData CONTENT", barcodeData)

        data = get_barcodes(barcodeData)
        data['measure']  = measure['measure']
        data['measure_w'] = measure['measure_w']
        data['measure_h'] = measure['measure_h']
        data['center_w'] = measure['center_w']
        data['path']  = path

    return data


def parse_text_data(text, measure, path):
    print("processing text ...")
    # Aquí va la lógica para extraer los datos del texto
    data = []
    res_rucs = None
    patterns_cli_igv = ["IGV 18", "I.G.V", "IGV"]
    patterns_cli_tot = ["IMPORTE TOTAL", "TOTAL S" , "TOTAL"]
    data_cia_ruc = ""
    data_cli_fac = ""
    data_cli_igv = ""
    data_cli_tot = ""
    data_cli_fec = ""
    data_cli_ruc = ""

    # print("\nTEXT", text)
    # FIND RUC
    res_rucs = re.findall("2\d{10,}", text)
    len_ruc = len(res_rucs)    
    if len_ruc>0:
        if len_ruc == 1:
            data_cia_ruc = res_rucs[0]
        elif len_ruc>1:
            data_cia_ruc = res_rucs[0]
            data_cli_ruc = res_rucs[1]
    # else:
    #     res_rucs = re.findall(r"RUC2[0-9]+(?:-[0-9]+)", text)
    #     print(".........res_rucs", res_rucs)
    #     # input(" .-.-. ")
    #     if len(res_rucs)>0:
    #         data_cia_ruc = str(res_rucs[0][3:]).split(" ")[0]
    
    # FIND BILL NUMBER
    res_bill_1 = re.search("[F,B]\d{3}", text)
    # print("\nFactura", res_bill_1)
    # res_bill_1 = re.findall("[F,E]\d{3}", text)
    # if len(res_bill_1) > 0:
    if res_bill_1 != None:
        data_cli_fac = str(text[res_bill_1.start(0):]).split("\n")[0]
        # data_cli_fac = res_bill_1[0]
    else:
        match = False
        res_bill_2 = re.search(" A\w{5,15}", text)
        if res_bill_2 != None:
            # res_bill_ = str(text[res_bill_2.start(0):]).split(" ")[0]
            res_bill_ = str(res_bill_2.group(0))[1:].split(" ")[0]
            match = re.search(r'[a-zA-Z]+', res_bill_) and re.search(r'[0-9]+', res_bill_)
            if match:
                data_cli_fac = res_bill_
    # FIND TOTAL
    for pattern in patterns_cli_tot :
        patt = re.search(rf"\b{pattern}", text, re.IGNORECASE)
        if patt != None :
            obj = str(text[patt.start(0):]).split("\n")[0].upper()
            if len(obj)>0:
                data_cli_tot = str(obj.split(pattern)[-1]).replace(" ","").replace(":","").replace("S","").replace("$","").replace("/","").replace("%","").replace("-","").replace("PAGADO","").replace("FACTURA","").replace("PAGAR","").replace("Y","")
                break
    # FIND IGV
    for pattern in patterns_cli_igv :
        patt = re.search(rf"{pattern}", text, re.IGNORECASE)
        if patt != None :
            obj = str(text[patt.start(0):]).split("\n")[0].upper()
            if len(obj)>0:
                data_cli_igv = str(obj.split(pattern)[-1]).replace(" ",'').replace(":",'').replace("%",'').replace("$",'').replace("/",'').replace("%",'').replace("-",'').replace("PAGADO","").replace("FACTURA","").replace("PAGAR","").replace("Y","")
                break
    data_cli_tot = str(data_cli_tot).replace('—','')
    # FIND DATE
    # data_cli_fec = ""
    # patterns_cli_fec.append(re.search(r'\d{2}/\d{2}/\d{4}', text))
    # patterns_cli_fec.append(re.search(r'\d{2}-\d{2}-\d{4}', text))
    # patterns_cli_fec.append(re.search(r'\d{4}/\d{2}/\d{2}', text))
    # patterns_cli_fec.append(re.search(r'\d{4}-\d{2}-\d{2}', text))
    # for pattern in patterns_cli_fec :
    #     if pattern != None:
    #         data_cli_fec = pattern.group(0)
    #         break
    
    # IS FULL
    barcode_isok = 2
    
    data = {
            'is_full':  barcode_isok,
            'cia_ruc':  data_cia_ruc,
            'cli_fac':  data_cli_fac,
            'cli_igv':  data_cli_igv,
            'cli_tot':  data_cli_tot,
            'cli_dat':  data_cli_fec,
            'cli_ruc':  data_cli_ruc,
            'currency': "S",
            'type_doc': "F",
            'measure':   measure['measure'],
            'measure_w': measure['measure_w'],
            'measure_h': measure['measure_h'],
            'center_w':  measure['center_w'],
            'path':     path
            }
    
    return data