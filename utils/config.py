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

# GLOBAL PARAMETERS
__C.GLOBAL = edict()
__C.GLOBAL.GLOBAL_PATH = GLOBAL_PATH
__C.GLOBAL.GLOBAL_TESS = GLOBAL_TESSERACT