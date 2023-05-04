from easydict import EasyDict as edict
import os

# PATH LOCAL
GLOBAL_PATH = os.path.abspath(os.getcwd())
GLOBAL_TESSERACT = r'/usr/local/bin/tesseract'
# PATH SERVER
# GLOBAL_PATH = '/var/www/webApp/webApp'
# GLOBAL_TESSERACT = r'/usr/bin/tesseract'

__C = edict()
cfg = __C

# PROCESS 
__C.PROCESS = edict()
__C.PROCESS.USE_GPU = False

# Percentage to change if posible to process service
__C.PROCESS.LIMIT_CPU = 90
__C.PROCESS.LIFE_TIME = 60 * 8

# GLOBAL PARAMETERS
__C.GLOBAL = edict()
__C.GLOBAL.GLOBAL_PATH = GLOBAL_PATH
__C.GLOBAL.GLOBAL_TESS = GLOBAL_TESSERACT

__C.GLOBAL.MAX_CONTENT_LENGTH = 40 * 1024 * 1024
__C.GLOBAL.UPLOAD_EXTENSIONS = ["PDF", "pdf"]
__C.GLOBAL.QR_EXTENSIONS    = ["PDF", "pdf", "JPG", "JPEG"]
__C.GLOBAL.QR_UPLOAD       = GLOBAL_PATH + '/files/qr_upload'
__C.GLOBAL.QR_IMAGES      = GLOBAL_PATH + '/files/qr_images'