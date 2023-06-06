from PIL import Image
from pyzbar import pyzbar
from utils.config import cfg
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader, PdfFileWriter
import datetime
import re
import os


def validate_path(path):
    new_path = path
    path_split = path.split("/")
    filename = path_split[-1]

    if filename[0] == "_":
        i = 0
        for c in filename:
            if c != filename[0]:
                pos = i
                break
            i += 1
        new_path = "/".join(path_split[:-1])+"/"+filename[pos:]

    return new_path

def split_img(path, files_split):
    result = False
    # pdf_reader = PdfFileReader(path)
    # box = pdf_reader.pages[0].mediaBox
    pdf_width = 580
    pdf_height = 800
    image = convert_from_path(path, dpi=300, size=(pdf_width, pdf_height))
    filename = files_split + '/' + str(path.split("/")[-1]).split(".")[0] + '.jpg'
    if image:
        image[0].save(filename,  format='JPEG', subsampling=0, quality=100)
        result = True

    return result, filename


def save_file(file):
    filename = secure_filename(file.filename)
    filename = filename.replace('(','').replace(')','').replace(',','').replace('<','').replace('>','').replace('?','').replace('!','').replace('@','').replace('%','').replace('$','').replace('#','').replace('*','').replace('&','').replace(';','').replace('{','').replace('}','').replace('[','').replace(']','').replace('|','').replace('=','').replace('+','').replace(' ','_')
    # Verify Image Name and Extension
    file_ext = filename.split(".")[-1]

    if (file_ext.upper()=='JPG' or  file_ext.upper()=='JPEG'):
        img = Image.open(file.stream)
        img_original = img
        image_width  = 0
        image_height = 0
        if int(img.width)>int(img.height):
            image_height = 540
            image_width = 800
        else:
            file_width  = img.width
            file_height = img.height
            fw = float(int(file_height) / int(file_width))
            if fw > 2.0:
                image_width = 400
                image_height = 800
            elif fw > 1.75:
                image_width = 460
                image_height = 800
            elif fw > 1.45:
                image_width = 540
                image_height = 800
            else:
                image_width = 580
                image_height = 800
        # SAVE and ready to read by QR
        path = os.path.join(cfg.GLOBAL.GLOBAL_PATH + '/files/qr_images', filename)
        img = img.resize((image_width, image_height), Image.ANTIALIAS)
        img.save(path, 'JPEG', quality=90)
        path = os.path.join('files/qr_images', filename)
    elif (file_ext.upper()=='PDF'):
        path = os.path.join(cfg.GLOBAL.GLOBAL_PATH + '/files/qr_upload', filename)
        path = validate_path(path)
        file.save(path)
        # Extract IMG, SAVE IMG and ready to read by QR
        result_pdf, filename = split_img(path, cfg.GLOBAL.GLOBAL_PATH + '/files/qr_images')
        if result_pdf == True:
            img = Image.open(filename)
            img_original = img
            filename = str(filename).split("/")[-1]
            path = os.path.join('files/qr_images', filename)
   
    return img_original, path


def parse_img_data(img):
    measure_dict = {}
    
    if int(img.width)>int(img.height):
        measure = "W"
        measure_h = "540px"
        measure_w = "800px"
        center_w = "0px"
    else:
        measure = "H"
        fw = float(int(img.height) / int(img.width))
        if fw > 2.0:
            measure_w = "400px"
            measure_h = "800px"
            center_w = "200px"
        elif fw > 1.75:
            measure_w = "460px"
            measure_h = "800px"
            center_w = "170px"
        elif fw > 1.45:
            measure_w = "540px"
            measure_h = "800px"
            center_w = "130px"
        else:
            measure_w = "580px"
            measure_h = "800px"
            center_w = "110px"
    
    measure_dict = {
                'measure':   measure,
                'measure_h': measure_h,
                'measure_w': measure_w,
                'center_w':  center_w
            }

    return measure_dict


def get_barcodes(barcodeData, list_bill):
    data = {}
    repeat = False
    band_ciaruc = False
    band_clitot = False
    band_clifac = False
    data['is_full'] = 3
    data['type_doc'] = ""
    data['currency'] = "S"
    data['cli_fac'] = ""
    data['cli_ruc'] = ""

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
                if code[0:1]=='NC':
                    data['type_doc'] = "NC"
                if code[0:1]=='ND':
                    data['type_doc'] = "ND"
                if code[0:1]=='RH':
                    data['type_doc'] = "RH"
                data['cli_fac'] = code
                band_clifac = True
                if data['cli_fac'] in list_bill:
                    repeat = True
                    break
            if len(code)==1 or len(code)==2:
                if int(code) == 1:
                    data['type_doc'] = "F"
            if len(code)>10 and str(code).count('-')==2:
                if data['type_doc'] == "":
                    data['type_doc'] = code[0]
                list_code = str(code).split('-')
                data['cli_fac'] = "F" + list_code[0] + '-' + list_code[2]
                if data['cli_fac'] in list_bill:
                    repeat = True
                    break
        else:
            data['cli_fac'] += '-' + code
            if data['cli_fac'] in list_bill:
                repeat = True
                break
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
        date_started = []
        date_complete = ""
        if len(code)==10 and (str(code).count('-')==2 or str(code).count('/')==2):
            date_started = str(code).split('-')
            if len(date_started)>1:
                if len(date_started[0])==2:
                    date_complete = str(code).replace("-", "/")
                if len(date_started[0])==4:
                    date_complete = datetime.datetime(int(date_started[0]), int(date_started[1]), int(date_started[2]))
                    date_complete = date_complete.strftime('%d/%m/%Y')
            date_started = str(code).split('/')
            if len(date_started)>1:
                if len(date_started[0])==2:
                    date_complete = code
                if len(date_started[0])==4:
                    date_complete = datetime.datetime(int(date_started[0]), int(date_started[1]), int(date_started[2]))
                    date_complete = date_complete.strftime('%d/%m/%Y')
            data['cli_dat'] = date_complete

    return data, repeat


def parse_qr_data(img, measure, path, list_bill):
    print("processing qr ...")
    # Aquí va la lógica para extraer los datos del código QR
    data = {}
    bill = ""
    barcodes = pyzbar.decode(img)
    # print("barcodes: ", barcodes)
        
    if len(barcodes) > 0 :
        # loop over the detected barcodes
        for barcode in barcodes:
            barcodeText = str(barcode.data.decode("utf-8"))
            barcodeData = barcodeText.split('|')
        print("\nbarcodeData LEN", len(barcodeData))
        print("barcodeData CONTENT", barcodeData)

        data, repeat = get_barcodes(barcodeData, list_bill)
        data['measure']  = measure['measure']
        data['measure_w'] = measure['measure_w']
        data['measure_h'] = measure['measure_h']
        data['center_w'] = measure['center_w']
        data['path']  = path
        if repeat == True:
            bill = data['cli_fac']

    return data, bill


def parse_text_data(text, measure, path, list_bill):
    print("processing text ...")
    # Aquí va la lógica para extraer los datos del texto
    data = {}
    bill = ""
    repeat = False
    res_rucs = None
    patterns_cli_igv = ["IGV 18", "I.G.V", "IGV"]
    patterns_cli_tot = ["IMPORTE TOTAL", "TOTAL S" , "TOTAL"]
    barcode_isok = 3
    data_cia_ruc = ""
    data_cli_ruc = ""
    data_cli_fac = ""
    data_cli_igv = ""
    data_cli_tot = ""
    data_cli_fec = ""
    data_cli_typ = ""

    # FIND BILL NUMBER
    res_bill_1 = re.search("[F,B]\d{3}", text)
    if res_bill_1 != None:
        data_cli_fac = str(text[res_bill_1.start(0):]).split("\n")[0]
        data_cli_fac = data_cli_fac.replace(" ","").replace("]","").replace("[","")
    else:
        match = False
        res_bill_2 = re.search(" A\w{5,15}", text)
        if res_bill_2 != None:
            res_bill_ = str(res_bill_2.group(0))[1:].split(" ")[0]
            match = re.search(r'[a-zA-Z]+', res_bill_) and re.search(r'[0-9]+', res_bill_)
            if match:
                data_cli_fac = res_bill_
                data_cli_fac = data_cli_fac.replace(" ","").replace("]","").replace("[","")

    if data_cli_fac != "":
        if data_cli_fac[0]=='F':
            data_cli_typ = "F"
        if data_cli_fac[0]=='B':
            data_cli_typ = "B"
        if data_cli_fac[0:1]=='NC':
            data_cli_typ = "NC"
        if data_cli_fac[0:1]=='ND':
            data_cli_typ = "ND"
        if data_cli_fac[0:1]=='RH':
            data_cli_typ = "RH"
        if data_cli_fac in list_bill:
            repeat = True
    
    if repeat == True:
        bill = data_cli_fac
    else:
        # FIND RUC
        res_rucs = re.findall("2\d{10,}", text)
        len_ruc = len(res_rucs)    
        if len_ruc>0:
            if len_ruc == 1:
                data_cia_ruc = res_rucs[0]
            elif len_ruc>1:
                data_cia_ruc = res_rucs[0]
                data_cli_ruc = res_rucs[1]            
        # FIND TOTAL
        for pattern in patterns_cli_tot :
            patt = re.search(rf"\b{pattern}", text, re.IGNORECASE)
            if patt != None :
                obj = str(text[patt.start(0):]).split("\n")[0].upper()
                if len(obj)>0:
                    data_cli_tot = str(obj.split(pattern)[-1]).replace(" ","").replace(":","").replace("S","").replace("$","").replace("/","").replace("%","").replace("-","").replace("PAGADO","").replace("FACTURA","").replace("PAGAR","").replace("Y","")
                    break
        data_cli_tot = re.sub("[^0123456789\.]","", data_cli_tot)
        # FIND IGV
        for pattern in patterns_cli_igv :
            patt = re.search(rf"{pattern}", text, re.IGNORECASE)
            if patt != None :
                obj = str(text[patt.start(0):]).split("\n")[0].upper()
                if len(obj)>0:
                    data_cli_igv = str(obj.split(pattern)[-1]).replace(" ",'').replace(":",'').replace("%",'').replace("$",'').replace("/",'').replace("%",'').replace("-",'').replace("PAGADO","").replace("FACTURA","").replace("PAGAR","").replace("Y","")
                    break
        data_cli_igv = re.sub("[^0123456789\.]","", data_cli_igv)
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
    
    if (data_cia_ruc != "" or data_cli_ruc != "" or data_cli_fac != "" or data_cli_igv != "" or data_cli_tot != ""):
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
            'type_doc':  data_cli_typ,
            'measure':   measure['measure'],
            'measure_w': measure['measure_w'],
            'measure_h': measure['measure_h'],
            'center_w':  measure['center_w'],
            'path':      path
            }
    
    return data, bill