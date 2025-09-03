import pytesseract
from PIL import Image
import io
import os
from config import TESSERACT_CMD_PATH, TESSDATA_PREFIX_PATH

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH

def extract_text_from_image(image_bytes):
    try:
        os.environ['TESSDATA_PREFIX'] = TESSDATA_PREFIX_PATH
        
        image = Image.open(io.BytesIO(image_bytes))
        
        text = pytesseract.image_to_string(image, lang='ukr+eng')
        
        return text
    except Exception as e:
        print(f"Error in OCR processing: {e}")
        return None