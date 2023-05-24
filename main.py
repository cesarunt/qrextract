from flask import Flask, request, render_template, send_from_directory
from flask import jsonify
from utils.concurrent import process_image, getting_text, rotate_image # process_images
from utils.qr import *
from utils.config import cfg
import time, json, os
from werkzeug.utils import secure_filename


main = Flask(__name__)

@main.route('/qr')
def qr():
    global results
    results = []
    return render_template('index.html')

@main.route('/qr', methods=['POST'])
def qr_post():
    global list_repeat
    global results
    global path_canvas
    global measure_canvas
    path_canvas = ""
    action = request.values.get("action")
    
    if action == "save_voucher":
        index = int(request.values.get("index"))-1
        results[index]['cli_dat']  = request.values.get("data_dat")
        results[index]['currency'] = request.values.get("data_cur")
        results[index]['type_doc'] = request.values.get("data_type")
        results[index]['cli_fac']  = str(request.values.get("data_bill")).upper()
        results[index]['cia_ruc']  = request.values.get("data_ciaruc")
        results[index]['cli_ruc']  = request.values.get("data_cliruc")
        results[index]['cli_tot']  = request.values.get("data_tot")
        results[index]['cli_igv']  = request.values.get("data_igv")
        results[index]['is_full']  = 1
        if path_canvas!="":
            results[index]['path']     = path_canvas
            results[index]['measure']  = measure_canvas
        return render_template('results.html', results=results, data_len=len(results), data_repeat=0)
    elif action == "get_canvas":
            index = int(request.values.get("index"))
            path = cfg.GLOBAL.GLOBAL_PATH + "/" + request.values.get("path")
            dictCanvas = json.loads(request.values.get("dictCanvas"))
            text_canvas = getting_text(path, dictCanvas)
            if text_canvas!="":
                return jsonify({'text_canvas': text_canvas})
            else:
                return jsonify({'text_canvas': "-"})
    elif action == "rotate_canvas":
            path_canvas = ""
            measure_canvas = ""
            index = int(request.values.get("index"))
            path = cfg.GLOBAL.GLOBAL_PATH + "/" + request.values.get("path")
            angle = request.values.get("angle")
            measure_current = request.values.get("measure_current")
            measure_w = request.values.get("measure_w")
            measure_h = request.values.get("measure_h")
            img_canvas, path_canvas, angle_canvas, measure_canvas, measure_width, measure_height = rotate_image(path, angle, measure_current, measure_w, measure_h)
            if img_canvas==True:
                return jsonify({'path_canvas': path_canvas, 
                                'angle_canvas': angle_canvas, 
                                'measure_canvas': measure_canvas,
                                'measure_width': measure_width,
                                'measure_height': measure_height
                                })
    elif action == "scan_voucher":
        # Format the path of Image
        path = cfg.GLOBAL.GLOBAL_PATH + request.values.get("path")
        print("path", path)
        img = Image.open(path)
        measure_current = request.values.get("measure_current")
        list_bill = []
        # Processs QR code
        measure = {
                    'measure':   measure_current,
                    'measure_h': 0,
                    'measure_w': 0,
                    'center_w':  0
                }
        data, _ = parse_qr_data(img, measure, path, list_bill)
        print("len data", len(data))
        print("len data", int(len(data)))
        if int(len(data))==0:
            return jsonify({'data_scan': "None"})
        else:
            return jsonify({'data_dat':     data['cli_dat'], 
                            'data_type':    data['type_doc'], 
                            'data_bill':    data['cli_fac'],
                            'data_ciaruc':  data['cia_ruc'],
                            'data_cliruc':  data['cli_ruc'],
                            'data_tot':     data['cli_tot'],
                            'data_igv':     data['cli_igv']
                            })
            
    else:
        if len(results)==0:
            start_time = time.time()
            files = request.files.getlist('files[]')
            results = []
            list_bill = []
            list_repeat = []
            for file in files:
                data, bill = process_image(file, list_bill)
                if bill != "":
                    list_repeat.append(bill)
                    continue
                elif len(data)>0:
                    list_bill.append(data['cli_fac'])
                    results.append(data)
            results = sorted(results, key=lambda d: d['is_full']) 

            print("Time:  --- %s seconds ---" % round(time.time() - start_time, 2))
            return render_template('results.html', results=results, data_len=len(results), data_repeat=len(list_repeat))
        else:
            print("Update list results without process")
            return render_template('results.html', results=results, data_len=len(results), data_repeat=len(list_repeat))


@main.route('/files/qr_upload/<filename>')
def qr_upload(filename):
    return send_from_directory(str(cfg.GLOBAL.GLOBAL_PATH+'/files/qr_upload'), filename)

@main.route('/files/qr_images/<filename>')
def qr_images(filename):
    return send_from_directory(str(cfg.GLOBAL.GLOBAL_PATH+'/files/qr_images'), filename)


if __name__ == '__main__':
    print("__main__")
    # start the flask app
    main.run(debug=True, use_reloader=True)
    # main.run(host="0.0.0.0", port="5000", debug=True, threaded=True, use_reloader=True)