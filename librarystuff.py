import rupasportread as pr
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

s = pr.catching('passport2.jpg')

print(s)