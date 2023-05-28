// Voucher number
_index = 0
// Length of data
_data_len = 0
var div_image
var div_canvasClass
var canvas_width
var canvas_height
var select_control
var inputFiles = document.getElementById("files");
var alert_wrapper = document.getElementById("alert_wrapper");
var process_wrapper = document.getElementById("process_wrapper");
var path_canvas

// ---------------------------
function showAlertPage(message, alert) {
  alert_wrapper.innerHTML = `
    <div id="alert_page" style="padding: 0.5rem 1rem;" class="alert alert-${alert} alert-dismissible fade show" role="alert" style="line-height:15px;">
      <small>${message}</small>
    </div>
  `
  etTimeout(function () {
    $('#alert_page').alert('close');
  }, 5000);
}

function updateVoucher(index, data_dat, data_type, data_bill, data_ciaruc, data_tot, data_igv) {
  div_item = document.getElementById("voucher_"+index)
  // Set green color by 5 seconds
  setTimeout(function () {
    div_item.style.backgroundColor = "#d4edda"
  }, 1000);
  setTimeout(function () {
    div_item.style.backgroundColor = ""
  }, 6000);
  //  Pass values on the item
  div_item.querySelector('#date').innerHTML=data_dat;
  div_item.querySelector('#doc_type').innerHTML=data_type;
  div_item.querySelector('#doc_number').innerHTML=data_bill;
  div_item.querySelector('#ruc_cia').innerHTML=data_ciaruc;
  div_item.querySelector('#total').innerHTML=data_tot;
  div_item.querySelector('#igv').innerHTML=data_igv;
  div_item.querySelector('#state').innerHTML='<span class="badge text-dark" style="background-color:rgb(0, 205, 0) !important; padding: 5px 2px;">[100%]</span>'
}

// Function to Show Progress QR
function clicQRProgress(_this) {
  // Reject if the file input is empty & throw alert
  if (!inputFiles.value) {
    // showAlertPage("Seleccione un archivo IMG / PDF", "warning");
    alert("Seleccione un archivo IMG / PDF")
    return;
  }
  else{
    // Hide the Cancel button
    _this.classList.add("d-none");
    // Show the load icon Process
    process_wrapper.classList.remove("d-none");
  }
}

// ZOOM FUNCTION
var bandZoom = false
var measure_last = "measure"
function activeZoom(_this, index) {
  console.log("Zoom......")
  if (div_image){
    div_image.classList.remove(measure_last);
  }

  if (bandZoom == false){
    div_modal = document.getElementById("exampleModal_"+index)
    div_image = div_modal.querySelector('#div_image');
    div_rotate = div_modal.querySelector('#div_items').querySelector("#btn_rotate")
    div_measure = div_modal.querySelector('#measure');
    div_canvasId = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector("#canvas")
    div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector(".upper-canvas")
    div_image.style.border = "2px dotted #00C";

    var points
    var pointX
    var pointY
    div_canvasClass.onclick = function(event) {
      points = event.target.getBoundingClientRect();
      pointX = event.clientX - points.left; //x position within the element.
      pointY = event.clientY - points.top;  //y position within the element.
      // console.log("X: " + pointX + "  Y: " + pointY);

      if (div_measure.value=='H'){
        if (pointY>400){
          div_image.classList.add("measure_hUp");
          measure_last = "measure_hUp"
        }
        else{
          div_image.classList.add("measure_hDw");
          measure_last = "measure_hDw"
        }
      }
      else {
        if (pointX>400){
          if (pointY>200){
            div_image.classList.add("measure_wRT");
            measure_last = "measure_wRT"
          }
          else{
            div_image.classList.add("measure_wRD");
            measure_last = "measure_wRD"
          }
        }
        else{
          if (pointY>200){
            div_image.classList.add("measure_wLT");
            measure_last = "measure_wLT"
          }
          else{
            div_image.classList.add("measure_wLD");
            measure_last = "measure_wLD"
          }
        }
      }
      _this.style.border = '2px dotted #00C'
      div_rotate.disabled = true
      bandZoom = true;
    }
  }
  else{
    div_image.style.border = "0";
    div_image.classList.remove(measure_last);
    div_rotate.disabled = false
    _this.style.border = '1px solid #17A2B8'
    bandZoom = false;
  }
}

// GET RUC NAME WITH API
// --------------------------------------------------------------------------------------------------
function getRUCName(url, index) {
  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();
  // Set the response type
  request.responseType = "json";
  div_modal = document.getElementById("exampleModal_"+index)
  div_ciaruc = div_modal.querySelector('#div_items').querySelector("#data_ciaruc")

  var action = "get_rucname";
  data.append("action", action);
  data.append("index", index);
  data.append("rucnumber", div_ciaruc.value);

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      rucname_canvas = request.response['rucname_canvas']
      if (rucname_canvas=="-"){
        rucname_canvas = "Número de RUC erróneo!"
        div_modal.querySelector('#div_items').querySelector("#data_cianame").style.color = "darkred"
        div_modal.querySelector('#div_items').querySelector("#data_cianame").innerHTML = rucname_canvas
      }
      else{
        div_modal.querySelector('#div_items').querySelector("#data_cianame").style.color = "darkblue"
        div_modal.querySelector('#div_items').querySelector("#data_cianame").innerHTML = rucname_canvas
      }
    }
    else {
        console.log('Nombre RUC no fue obtenido')
    }    
  });
  // request error handler
  request.addEventListener("error", function (e) {
    alert(`Error reading API service`, "danger");
  });
  // Open and send the request
  request.open("POST", url);
  request.send(data);
}

// ROTATE FUNCTION
// --------------------------------------------------------------------------------------------------
function makeRotate(url, measure_w, measure_h, index, path) {
  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();
  // Set the response type
  request.responseType = "json";
  div_modal = document.getElementById("exampleModal_"+index)
  div_image = div_modal.querySelector('#div_image');
  div_measure = div_modal.querySelector('#measure');
  div_angle = div_modal.querySelector('#angle');

  path_canvas = ""
  var action = "rotate_canvas";
  data.append("action", action);
  data.append("index", index);
  data.append("path", path);
  data.append("measure_current", div_measure.value);
  data.append("measure_w", measure_w);
  data.append("measure_h", measure_h);
  data.append("angle", div_angle.value);

  // request load handler (transfer complete)
  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      path_canvas = request.response['path_canvas']
      angle_canvas = request.response['angle_canvas']
      measure_canvas = request.response['measure_canvas']
      measure_width = request.response['measure_width']
      measure_height = request.response['measure_height']

      div_angle.value = angle_canvas
      div_measure.value = measure_canvas
      div_canvasId = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector("#canvas")
      div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector(".upper-canvas")
      var measureW
      var centerLf
      measureW = measure_width
      measure_width = measure_width.toString() + "px"
      measure_height = measure_height.toString() + "px"

      if (measure_canvas=='W'){
        div_canvasId.style.width = measure_width;
        div_canvasClass.style.width = measure_width;
        div_canvasId.style.height = measure_height;
        div_canvasClass.style.height = measure_height;
        div_canvasId.style.left = "0px";
        div_canvasClass.style.left = "0px";
        div_canvasId.parentNode.style.height = "500px"
      }
      else {
        div_canvasId.style.height = measure_height;
        div_canvasClass.style.height = measure_height;
        div_canvasId.style.width = measure_width;
        div_canvasClass.style.width = measure_width;
        if (measureW==400){ centerLf = "200px" }
        if (measureW==460){ centerLf = "170px" }
        if (measureW==540){ centerLf = "130px" }
        if (measureW==580){ centerLf = "110px" }
        div_canvasId.style.left = centerLf;
        div_canvasClass.style.left = centerLf;
        div_canvasId.parentNode.style.height = "800px"
      }
      $(div_canvasId).css({ 'background-image': 'url('+ path_canvas +')', 'background-repeat': 'no-repeat', 'background-size': 'cover' });
      $(div_canvasClass).css({ 'background-image': 'url('+ path_canvas +')', 'background-repeat': 'no-repeat', 'background-size': 'cover' });      
    }
    else {
        console.log('Canvas no fue actualizado')
    }    
  });
  // request error handler
  request.addEventListener("error", function (e) {
    alert(`Error procesando la imagen`, "danger");
  });
  // Open and send the request
  request.open("POST", url);
  request.send(data);
}

// -----------------------------------------------------------------------------------------------------
var bandScan = false
function scanQR(_this, url, index, path) {
  if (bandScan == false){
    div_modal = document.getElementById("exampleModal_"+index)
    div_image = div_modal.querySelector('#div_image');
    div_rotate = div_modal.querySelector('#div_items').querySelector("#btn_rotate")
    div_measure = div_modal.querySelector('#measure');
    div_canvasId = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector("#canvas")
    div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector(".upper-canvas")
    div_image.style.border = "2px dotted #00C";

    // Create a new FormData instance
    var data = new FormData();
    // Create a XMLHTTPRequest instance
    var request = new XMLHttpRequest();
    // Set the response type
    request.responseType = "json";
    if (path!=""){ path_canvas = path }

    var action = "scan_voucher";
    data.append("action", action);
    data.append("index", index);
    data.append("path", path_canvas)
    data.append("measure_current", div_measure.value);

    request.addEventListener("load", function (e) {
      if (request.status == 200) {
        data_scan = request.response['data_scan']
        if (data_scan=="None"){
          alert("No se detectó QR")
        }
        else{
          data_dat  = request.response['data_dat']
          data_type = request.response['data_type']
          data_bill = request.response['data_bill']
          data_ciaruc = request.response['data_ciaruc']
          data_cliruc = request.response['data_cliruc']
          data_tot = request.response['data_tot']
          data_igv = request.response['data_igv']
          div_modal.querySelector('#div_items').querySelector("#data_dat").value = data_dat
          div_modal.querySelector('#div_items').querySelector("#data_type").value = data_type
          div_modal.querySelector('#div_items').querySelector("#data_bill").value = data_bill
          div_modal.querySelector('#div_items').querySelector("#data_ciaruc").value = data_ciaruc
          div_modal.querySelector('#div_items').querySelector("#data_cliruc").value = data_cliruc
          div_modal.querySelector('#div_items').querySelector("#data_tot").value = data_tot
          div_modal.querySelector('#div_items').querySelector("#data_igv").value = data_igv
          alert("Voucher escaneado con éxito")
        }
      }
      if (request.status == 300) {
        alert('Warming on Voucher')
        // showAlertPage(`${request.response.message}`, 'warning')
      }
    });
    // request error handler
    request.addEventListener("error", function (e) {
      showAlertPage('Error escaneando voucher', 'danger')
    });
    // Open and send the request
    request.open("POST", url);
    request.send(data);
    }
}

// --------------------------------------------------------------------------------------------------------
function saveVoucher(_this, url, index) {
  console.log("save Voucher")
  var data_dat  = _this.parentNode.parentNode.querySelector('#data_dat')
  var data_cur  = _this.parentNode.parentNode.querySelector('#data_cur')
  var data_type = _this.parentNode.parentNode.querySelector('#data_type')
  var data_bill = _this.parentNode.parentNode.querySelector('#data_bill')
  var data_ciaruc = _this.parentNode.parentNode.querySelector('#data_ciaruc')
  var data_cliruc = _this.parentNode.parentNode.querySelector('#data_cliruc')
  var data_tot  = _this.parentNode.parentNode.querySelector('#data_tot')
  var data_igv  = _this.parentNode.parentNode.querySelector('#data_igv')

  // Reject if the file input is empty & throw alert
  if (!data_dat.value)  { alert("Debe ingresar fecha", "warning"); return; }
  if (!data_cur.value)  { alert("Debe seleccionar moneda", "warning"); return; }
  if (!data_type.value) { alert("Debe seleccionar tipo Documento", "warning"); return; }
  if (!data_bill.value) { alert("Debe ingresar No Documento", "warning"); return; }
  if (!data_ciaruc.value) { alert("Debe ingresar RUC empresa", "warning"); return; }
  if (data_ciaruc.value.length != 11) { alert("RUC Empresa debe tener 11 digitos", "warning"); return; }
  if (!data_cliruc.value) { alert("Debe ingresar RUC cliente", "warning"); return; }
  if (data_cliruc.value.length != 11) { alert("RUC Cliente debe tener 11 digitos", "warning"); return; }
  if (!data_tot.value)  { alert("Debe ingresar total", "warning"); return; }
  if (!data_igv.value)  { alert("Debe ingresar IGV", "warning"); return; }

  // Create a new FormData instance
  var data = new FormData();
  // Create a XMLHTTPRequest instance
  var request = new XMLHttpRequest();
  // Set the response type
  request.responseType = "json";

  var action = "save_voucher";
  data.append("action", action);
  data.append("index", index)
  data.append("data_dat", data_dat.value);
  data.append("data_cur", data_cur.value);
  data.append("data_type", data_type.value);
  data.append("data_bill", data_bill.value);
  data.append("data_ciaruc", data_ciaruc.value);
  data.append("data_cliruc", data_cliruc.value);
  data.append("data_tot", data_tot.value);
  data.append("data_igv", data_igv.value);

  request.addEventListener("load", function (e) {
    if (request.status == 200) {
      // div_modal = document.getElementById("exampleModal_"+index)
      // div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector(".upper-canvas")
      // div_canvasClass.remove()
      // showAlertPage('Voucher registrado con éxito', 'success')
      alert("Voucher registrado con éxito")
      closeVoucher(index)
      updateVoucher(index, data_dat.value, data_type.value, data_bill.value, data_ciaruc.value, data_tot.value, data_igv.value)
      // div_modal.setAttribute("style", `display: `);
    }
    else {
      showAlertPage('Voucher no fue registrado', 'warning')
    }
    if (request.status == 300) {
      showAlertPage(`${request.response.message}`, 'warning')
    }
  });
  // request error handler
  request.addEventListener("error", function (e) {
    showAlertPage('Error registrando voucher', 'danger')
  });
  // Open and send the request
  request.open("POST", url);
  request.send(data);
}

var canvas;
var arrow;
var ctx;

// ACTION in order to OPEN voucher details
function openVoucher(_this, index, data_len, center_w) {
  _index = index
  _data_len = data_len
  div_modal = document.getElementById("exampleModal_"+index)
  div_canvasId = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector("#canvas")
  div_image = div_modal.querySelector('#div_image');
  div_measure = div_modal.querySelector('#measure');

  if (div_canvasClass){
    div_canvasClass.remove()
  }
  canvas_width = div_canvasId.width
  canvas_height = div_canvasId.height
  
  canvas = new fabric.Canvas(div_canvasId);
  arrow = new Rectangle(canvas);
  ctx = canvas.getContext("2d");
  div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").getElementsByClassName("upper-canvas")[0]

  if (parseInt(canvas_width)>parseInt(canvas_height)){
    measure_max = canvas_width
    measure_min = canvas_height
  }
  else{
    measure_max = canvas_height
    measure_min = canvas_width
  }
  measure_max = measure_max.toString() + "px"
  measure_min = measure_min.toString() + "px"

  if (div_measure.value=='W'){
    // div_canvasId.width = measure_max //
    div_canvasId.style.width = measure_max;
    // div_canvasClass.width = measure_max //
    div_canvasClass.style.width = measure_max;
    // div_canvasId.height = measure_min //
    div_canvasId.style.height = measure_min;
    // div_canvasClass.height = measure_min //
    div_canvasClass.style.height = measure_min;
    div_canvasId.style.left = "0px";
    div_canvasClass.style.left = "0px";
    div_canvasId.parentNode.style.height = "480px"
  }
  else {
    // div_canvasId.height = measure_max //
    div_canvasId.style.height = measure_max;
    // div_canvasClass.height = measure_max //
    div_canvasClass.style.height = measure_max;
    // div_canvasId.width = measure_min //
    div_canvasId.style.width = measure_min;
    // div_canvasClass.width = measure_min //
    div_canvasClass.style.width = measure_min;
    div_canvasId.style.left = center_w;
    div_canvasClass.style.left = center_w;
    div_canvasId.parentNode.style.height = "800px"
  }
}

// ACTION in order to CLOSE voucher details
function closeVoucher(index) {
  document.getElementById("exampleModal_"+index).classList.remove("show");
  elements = document.getElementsByClassName("modal-backdrop");
  while (elements.length > 0) elements[0].remove();
  document.getElementById("exampleModal_"+index).setAttribute("style", "display: inherit;");
}

// ACTION in order to MOVE voucher down & up
function moveVoucher(_this, index, direct) {
  if (parseInt(index) >= 0 && parseInt(index) <= parseInt(_data_len)+1){
    if (direct == "up"){
      _index = (parseInt(index) + 1).toString()
    }
    if (direct == "down"){
      _index = (parseInt(index) - 1).toString()
    }
  }

  if (parseInt(_index) > 0 && parseInt(_index) < parseInt(_data_len)+1){
    document.getElementById("exampleModal_"+index).classList.remove("show");
    document.getElementById("exampleModal_"+index).setAttribute("style", `display: `);
    div_modal = document.getElementById("exampleModal_"+_index)
    div_canvasId = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").querySelector("#canvas")
    div_measure = div_modal.querySelector('#measure');

    if (div_canvasClass){
      div_canvasClass.remove()
    }
    canvas_width = div_canvasId.width
    canvas_height = div_canvasId.height

    canvas = new fabric.Canvas(div_canvasId);
    arrow = new Rectangle(canvas);
    ctx = canvas.getContext("2d");
    div_canvasClass = div_modal.querySelector("#canvasContainer").querySelector("#canvasContainer").getElementsByClassName("upper-canvas")[0]

    if (parseInt(canvas_width)>parseInt(canvas_height)){
      measure_max = canvas_width
      measure_min = canvas_height
    }
    else{
      measure_max = canvas_height
      measure_min = canvas_width
    }
    measure_max = measure_max.toString() + "px"
    measure_min = measure_min.toString() + "px"

    if (div_measure.value=='W'){
      div_canvasId.style.width = measure_max;
      div_canvasClass.style.width = measure_max;
      div_canvasId.style.height = measure_min;
      div_canvasClass.style.height = measure_min;
      div_canvasId.style.left = "0px";
      div_canvasClass.style.left = "0px";
      div_canvasId.parentNode.style.height = "480px"
    }
    else {
      div_canvasId.style.height = measure_max;
      div_canvasClass.style.height = measure_max;
      div_canvasId.style.width = measure_min;
      div_canvasClass.style.width = measure_min;
      if (measure_min=="400px"){ centerLf = "200px" }
      if (measure_min=="460px"){ centerLf = "170px" }
      if (measure_min=="540px"){ centerLf = "130px" }
      if (measure_min=="580px"){ centerLf = "110px" }
      div_canvasId.style.left = centerLf;
      div_canvasClass.style.left = centerLf;
      div_canvasId.parentNode.style.height = "800px"
    }
    div_modal.classList.add("show");
    div_modal.setAttribute("style", `display: block`);
  }
}

function validateNumbers(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  key = String.fromCharCode( key );
  var regex = /[0-9]/;
  if( !regex.test(key) ) {
    theEvent.returnValue = false;
    if(theEvent.preventDefault) theEvent.preventDefault();
  }
}

function validateAlphanumerics(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  key = String.fromCharCode( key );
  var regex = /[a-zA-Z0-9]|\-/;
  if( !regex.test(key) ) {
    theEvent.returnValue = false;
    if(theEvent.preventDefault) theEvent.preventDefault();
  }
}