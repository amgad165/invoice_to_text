from PIL import Image
import pytesseract
import argparse
import cv2
import os
import imutils
import pandas as pd
import re
from pdf2image import convert_from_path
from docx import Document

# pytesseract.pytesseract.tesseract_cmd = r'E:\Python Workspace\Freelancer\AI image to text web based project\Tesseract-OCR\tesseract.exe'


def img_to_df(image_path):
    
    pytesseract.pytesseract.tesseract_cmd = r'E:\Python Workspace\Freelancer\AI image to text web based project\Tesseract-OCR\tesseract.exe'
    
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_img = clahe.apply(img)
    threshold_value, img = cv2.threshold(enhanced_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    text = pytesseract.image_to_string(img,config='--psm 4')
    # Split the text into lines
    lines = text.split('\n')
    info_list = []
    date_pattern = r'(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})|([a-zA-Z]{3}\s\d{1,2}[,]?\s\d{4})|(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})|(\d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4})|(\d{1,2}/\d{2})'
    regex_description = r"[A-Za-z\s,.:;/()&]{3,}"
    regex_amount = r'[-]?\d{1,3}(?:,\d{3})*\.\d{2}|\$\d+(?:\.\d+)?'

    # Loop over the lines and extract information using regular expressions
    for i in range(len(lines)):
        # Extract date
        date_match = re.search(date_pattern, lines[i])
        # Extract description and amount
        description_match = re.search(regex_description, lines[i])
        amount_match = re.findall(regex_amount, lines[i])
        if date_match:
            date = date_match.group()
            if description_match and amount_match:
                description = description_match.group().strip()
    #             amount = amount_match.group().strip()
                info_list.append([date, description,amount_match])
            elif amount_match:
                description = ''
                info_list.append([date, description,amount_match])
        elif description_match and amount_match:
            date = ''
            description = description_match.group().strip()
            info_list.append([date, description,amount_match])
    df = pd.DataFrame(info_list, columns=['Date', 'Description', 'Money details'])
    df['Money details'] = df['Money details'].apply(lambda x: ', '.join(x))
    return df

def img_to_text(image_path):
    
    pytesseract.pytesseract.tesseract_cmd = r'E:\Python Workspace\Freelancer\AI image to text web based project\Tesseract-OCR\tesseract.exe'
    
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    # gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced_img = clahe.apply(img)
    threshold_value, img = cv2.threshold(enhanced_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    text = pytesseract.image_to_string(img)
    return text


def pdf_to_text(pdf_path):
    
    pytesseract.pytesseract.tesseract_cmd = r'E:\Python Workspace\Freelancer\AI image to text web based project\Tesseract-OCR\tesseract.exe'
    
    doc = convert_from_path(pdf_path, 500,poppler_path=r'C:\Program Files\poppler-0.68.0\bin')
    final_text = ''
    for count, img in enumerate(doc):
        extracted_text = pytesseract.image_to_string(img)
        page_count = '\n Page '+str(count+1)+'\n\n'
        final_text += page_count + str(extracted_text)
    return final_text
