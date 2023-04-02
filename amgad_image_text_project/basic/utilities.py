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

    text = pytesseract.image_to_string(img,config='--psm 4')


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


def search_for_bank(string):
    if "bank" in string.lower():
        return True
    else:
        return False
    
def get_table_headers(invoice_text, header_pattern,word_pattern):
    """Find the location of the table header in the invoice text."""
    invoice_text = invoice_text.lower()

    max_keyword_count = 0
    max_keyword_text = ""
    max_keyword_header_end = 0

    # Find the header row with the most keywords
    for match in re.finditer(header_pattern, invoice_text):
        header_end = match.end()
        header_start = invoice_text.rfind("\n", 0, header_end) + 1    
        header_row = invoice_text[header_start:header_end]

        # Count the number of keywords found in the header row
        keyword_count = len(re.findall(fr'({word_pattern})', header_row, re.IGNORECASE))

        # If this header row has more keywords than any previous header row, save it
        if keyword_count > max_keyword_count:
            max_keyword_count = keyword_count
            max_keyword_text = header_row
            max_keyword_header_end = header_end

    # Find the header row(s) with the most keywords, starting from the end of the invoice text
    for match in reversed(list(re.finditer(header_pattern, invoice_text))):  # Reverse the order of matches
        header_end = match.end()
        text_after_header = invoice_text[header_end:]
        keyword_count = len(re.findall(fr'({word_pattern})', text_after_header, re.IGNORECASE))

        if keyword_count == max_keyword_count:
            # If this header row has the same number of keywords as the previous row(s), add it to the list
            max_keyword_text += text_after_header
            max_keyword_header_end = header_end
        else:
            # Otherwise, we're done (since we're going in reverse order)
            break

    # Print the result(s)
    if not max_keyword_text:
        print("No matching header rows found.")
    else:
#         print(f"Found header row(s) with the most ({max_keyword_count}) keywords:")
#         print(max_keyword_text)
#         print(f"Header end: {max_keyword_header_end}")
        return max_keyword_text,max_keyword_header_end


def get_header_keywords(header_row, header_keywords):
    """Check if header keywords exist in the header row and return the relevant ones."""
#     header_row = re.sub(r"[^\w/\\]+", " ", header_row)
    header_row = re.sub(r"(?<![^\W_])[\W_]+(?![^\W_])", " ", header_row)
    for keyword in header_keywords:
        if keyword in header_row.lower():
            header_row = header_row.replace(keyword, keyword.replace(' ', '_'))
            
            
    found_keywords = header_row.split()

    return found_keywords



def get_invoice_data(invoice_text, header_end, row_pattern, found_keywords):
    """Extract table data and return as a list of lists."""
    table_data = []
    row_matches = row_pattern.findall(invoice_text[header_end:])
    for row_match in row_matches:
        
        regex_description = r"[A-Za-z\s,.:;/()&]{3,}"
        regex_amount = r'[-]?\d{1,3}(?:,\d{3})*\.\d{2}|\$?\d{1,3}(?:,\d{3})*\.\d{2}|\$\d+(?:\.\d+)?|\b\d+\b'
        date_pattern = r'(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})|([a-zA-Z]{3}\s\d{1,2}[,]?\s\d{4})|(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})|(\d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4})|(\d{1,2}/\d{2})'
        description= ''
        date = None
        amount_match = ''
        try:
            description_match = re.search(regex_description, row_match)
            description = description_match.group().strip()
            description = re.sub(r"[^\w/\\\s]+", "", description)
        except:
            pass  
        try:
            date_match = re.search(date_pattern, row_match)
            date = date_match.group()
        except:
            pass

        try:           
            amount_match = re.findall(regex_amount, row_match)
        except:
            pass  
        
        # getting the data by regular expression method
        if (date):
            cols=[date]+[description]+amount_match
        else:
            cols=[description]+amount_match
            
        #getting the data by splitting method
        row_splitted = row_match.split(' ')
        # diff between the number of col got from regex method,split method and number of col from headers
        col_header_diff = abs(len(cols)-len(found_keywords))
        split_header_diff = abs(len(row_splitted)-len(found_keywords))
        descrip_split = description.split(' ')
        
        #getting the data by splitting method
        row_splitted = row_match.split(' ')
        # diff between the number of col got from regex method,split method and number of col from headers
        col_header_diff = abs(len(cols)-len(found_keywords))
        split_header_diff = abs(len(row_splitted)-len(found_keywords))
        descrip_split = description.split(' ')   
        
        
        if len(cols) == len(found_keywords):
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)

        #check the splitted row 
        elif len(row_splitted) == len(found_keywords):
            if len(row_splitted)>1:
                if (amount_match):
                    table_data.append(row_splitted)
                    
        elif len(descrip_split)==2 and len(cols)<len(found_keywords):
            
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)
            
        elif split_header_diff<col_header_diff and len(descrip_split)<3:
            if len(row_splitted)>1:
                if (amount_match):
                    
                    table_data.append(row_splitted)
        else:
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)

            
        # Check if enough header keywords were found    



    return table_data, found_keywords

def get_bank_data(invoice_text, header_end, row_pattern, found_keywords):
    """Extract table data and return as a list of lists."""
    table_data = []
    row_matches = row_pattern.findall(invoice_text[header_end:])
    for row_match in row_matches:
        # Split the row into columns
#         cols = re.findall(r"\w+[\w\s]*|\$[\d\.]+|\d+", row_match)
#         cols = re.findall(r"[A-Za-z\s,.:;/()&]{3,}", row_match)
        regex_description = r"[A-Za-z\s,.:;/()&]{3,}"
        regex_amount = r'[-]?\d{1,3}(?:,\d{3})*\.\d{2}|\$?\d{1,3}(?:,\d{3})*\.\d{2}|\$\d+(?:\.\d+)?'
        date_pattern = r'(\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4})|([a-zA-Z]{3}\s\d{1,2}[,]?\s\d{4})|(\d{4}[-/\.]\d{1,2}[-/\.]\d{1,2})|(\d{2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4})|(\d{1,2}/\d{2})'
        description= ''
        date = ''
        amount_match = ''
        try:
            description_match = re.search(regex_description, row_match)
            description = description_match.group().strip()
            description = re.sub(r"[^\w/\\\s]+", "", description)
            
        except:
            pass      
        
        try:
            date_match = re.search(date_pattern, row_match)
            date = date_match.group()
        except:
            pass      
        try:           
            amount_match = re.findall(regex_amount, row_match)
        except:
            pass       
        
        cols=[date]+[description]+amount_match
            
        #getting the data by splitting method
        row_splitted = row_match.split(' ')
        # diff between the number of col got from regex method,split method and number of col from headers
        col_header_diff = abs(len(cols)-len(found_keywords))
        split_header_diff = abs(len(row_splitted)-len(found_keywords))
        descrip_split = description.split(' ')   
        
        
        if len(cols) == len(found_keywords):
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)

        #check the splitted row 
        elif len(row_splitted) == len(found_keywords):
            if len(row_splitted)>1:
                if (amount_match):
                    table_data.append(row_splitted)
                    
        elif len(descrip_split)==2 and len(cols)<len(found_keywords):
            
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)
            
        elif split_header_diff<col_header_diff and len(descrip_split)<3:
            if len(row_splitted)>1:
                if (amount_match):
                    
                    table_data.append(row_splitted)
        else:
            if len(cols)>1:            
                if (amount_match):
                    table_data.append(cols)

            
        # Check if enough header keywords were found    



    return table_data, found_keywords




def extract_bank_df(invoice_text):
    # Define the header keywords that will be filtered if found in the tables
    edit_keywords = ['price per unit','unit price','qty/ hr','user balance'] 

    # Define regex patterns for matching table headers and rows
    # header_pattern = re.compile(r"(?<=\n)description(?=\s+[A-Za-z]+)")

#     header_pattern = re.compile(r".*date.*")
    # Construct the regular expression to search for at least two words in the list
    
    bank_statment_keywords = ['pate','date','description','Credit','Balance','Fee','Deposit','Payment','amount']
    word_pattern = '|'.join(bank_statment_keywords)
    header_pattern = re.compile(fr'(?=.*({word_pattern})).*', re.IGNORECASE)
    
#     header_pattern = re.compile(fr'(?=.*({word_pattern})).*', re.IGNORECASE)
    row_pattern = re.compile(r"(?<=\n).+(?=\n)")

    # Find the location of the table header in the invoice text
    header_row,header_end = get_table_headers(invoice_text, header_pattern,word_pattern)

    # Get the relevant header keywords
    found_keywords = get_header_keywords(header_row, edit_keywords)

    # Extract the table data
#     header_end = header_pattern.search(invoice_text).end()
    table_data, found_keywords = get_bank_data(invoice_text, header_end, row_pattern, found_keywords)

    # Create a pandas dataframe with the table data


    # Add extra columns to found_keywords if necessary
    if len(table_data) > 0:
        max_cols = max(len(row) for row in table_data)
        num_extra_cols = max(0, max_cols - len(found_keywords))
        extra_cols = ['others {}'.format(i+1) for i in range(num_extra_cols)]
        found_keywords += extra_cols

    # Fill remaining columns with blank
    for i in range(len(found_keywords) - len(table_data[0])):
        table_data[0].append('')
        
    df = pd.DataFrame(table_data, columns=found_keywords)
    df = df.fillna('')
    return df



def extract_invoice_df(invoice_text):
    # Define the header keywords that will be filtered if found in the tables
    edit_keywords = ['price per unit','unit price','qty/ hr','date   time','dialled number']

    # Define regex patterns for matching table headers and rows
    # header_pattern = re.compile(r"(?<=\n)description(?=\s+[A-Za-z]+)")
    
    invoice_keywords = ['description','items','quantity', 'price','unit price','subtotal','tax ','discount','total amount','destination','cost','money']
    word_pattern = '|'.join(invoice_keywords)
    header_pattern = re.compile(fr'(?=.*({word_pattern})).*', re.IGNORECASE)
    
#     header_pattern = re.compile(fr'(?=.*({word_pattern})).*', re.IGNORECASE)
    row_pattern = re.compile(r"(?<=\n).+(?=\n)")

    # Find the location of the table header in the invoice text
    header_row,header_end = get_table_headers(invoice_text, header_pattern,word_pattern)

    # Get the relevant header keywords
    found_keywords = get_header_keywords(header_row, edit_keywords)
    # Extract the table data
#     header_end = header_pattern.search(invoice_text).end()
    table_data, found_keywords = get_invoice_data(invoice_text, header_end, row_pattern, found_keywords)

    # Create a pandas dataframe with the table data


    # Add extra columns to found_keywords if necessary
    if len(table_data) > 0:
        max_cols = max(len(row) for row in table_data)
        num_extra_cols = max(0, max_cols - len(found_keywords))
        extra_cols = ['others {}'.format(i+1) for i in range(num_extra_cols)]
        found_keywords += extra_cols

    # Fill remaining columns with blank
    for i in range(len(found_keywords) - len(table_data[0])):
        table_data[0].append('')
    df = pd.DataFrame(table_data, columns=found_keywords)
    df = df.fillna('')
    return df

