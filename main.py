from flask import Flask, request, render_template, redirect, send_from_directory
from flask import jsonify
from utils.concurrent import process_images, getting_text
from utils.qr import *
import time
import json

GLOBAL_PATH = os.path.abspath(os.getcwd())

main = Flask(__name__)

@main.route('/')
def index():
    global results
    results = []
    return render_template('index.html')

# OPTION 1
# @main.route('/upload', methods=['POST'])
# def upload():
#     files = request.files.getlist("file")
#     results = []

#     for file in files:
#         img = Image.open(file.stream)

#         # Procesar el código QR
#         qr_data = decode(img)
#         if qr_data:
#             results.append(parse_qr_data(qr_data))
#         else:
#             # Extraer texto de la imagen
#             text = pytesseract.image_to_string(img)

#             # Buscar datos en el texto
#             results.append(parse_text_data(text))

#     return render_template('results.html', results=results)

# OPTION 2
@main.route('/upload', methods=['POST'])
def upload():
    global results
    action = request.values.get("action")
    
    if action == "save_voucher":
        index = int(request.values.get("index"))-1
        results[index]['cli_dat']  = request.values.get("data_dat")
        results[index]['currency'] = request.values.get("data_cur")
        results[index]['type']     = request.values.get("data_type")
        results[index]['cli_fac']  = request.values.get("data_bill")
        results[index]['cia_ruc']  = request.values.get("data_ciaruc")
        results[index]['cli_ruc']  = request.values.get("data_cliruc")
        results[index]['cli_tot']  = request.values.get("data_tot")
        results[index]['cli_igv']  = request.values.get("data_igv")
        results[index]['is_full']  = 1
        return render_template('results.html', results=results, data_len=len(results))
    
    elif action == "get_canvas":
            index = int(request.values.get("index"))
            path = GLOBAL_PATH + "/" + request.values.get("path")
            dictCanvas = json.loads(request.values.get("dictCanvas"))
            text_canvas = getting_text(path, dictCanvas)
            if text_canvas!="":
                return jsonify({'text_canvas': text_canvas})
            else:
                return jsonify({'text_canvas': "-"})

    else:
        if len(results)==0:
            files_size = request.files['files[]'].read()
            if len(files_size) > 0:
                start_time = time.time()
                files = request.files.getlist("files[]")
                results = process_images(files)
                print("Time:  --- %s seconds ---" % round(time.time() - start_time, 2))
                return render_template('results.html', results=results, data_len=len(results))
            else:
                url = str(request.url).split('/upload')[0]
                return redirect(url)
        else:
            print("Update list results without process")
            return render_template('results.html', results=results, data_len=len(results))


@main.route('/files/upload/<filename>')
def upload_img(filename):
    return send_from_directory(GLOBAL_PATH+'/files/upload', filename)

# OPTION 3
# @app.route('/upload', methods=['POST'])
# def upload():
#     files = [request.files[file_key] for file_key in request.files]
#     results = process_images(files)
#     return jsonify(results)

if __name__ == '__main__':
    print("__main__")
    # start the flask app
    main.run(debug=True, use_reloader=True)