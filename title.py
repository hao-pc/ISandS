import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
tessdata_dir_config = r'C:/Program Files/Tesseract-OCR/tessdata'

pdf_path = 'свидетельство.pdf'
images = convert_from_path(pdf_path=pdf_path, poppler_path='C:/poppler-24.08.0/Library/bin')

for image in images:
    text = pytesseract.image_to_string(image, lang='rus', config=tessdata_dir_config).lower().replace('\n', ' ').replace('  ', ' ').strip()
    print(text)
    # if 'информация о поступлении и расходовании денежных средств омс' in text:
    #     print(True)
    # else:
    #     print(False)