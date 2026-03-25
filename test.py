import pytesseract
import os

base = os.path.join(os.getcwd(), "Tesseract")

pytesseract.pytesseract.tesseract_cmd = os.path.join(base, "tesseract.exe")

os.environ["TESSDATA_PREFIX"] = os.path.join(base, "tessdata")

print(pytesseract.get_tesseract_version())