import fitz  # PyMuPDF
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
import spacy
import pdfplumber
import csv
import json
from concurrent.futures import ThreadPoolExecutor

# Function to extract text from PDF using pdfplumber for layout analysis
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to preprocess image for better OCR results
def preprocess_image(image):
    # Convert to grayscale
    image = image.convert("L")
    # Increase contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)
    # Remove noise
    image = image.filter(ImageFilter.MedianFilter())
    return image

# Function to extract images from PDF and perform OCR with parallel processing
def extract_images_and_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_text = ""
    
    def process_image(page_num):
        page_ocr_text = ""
        for img in doc.get_page_images(page_num):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            preprocessed_image = preprocess_image(image)
            page_ocr_text += pytesseract.image_to_string(preprocessed_image)
        return page_ocr_text
    
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_image, range(len(doc)))
        ocr_text = ''.join(results)
    
    return ocr_text

# Function to extract requirements using rule-based parsing with keyword and pattern matching
def extract_requirements(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    requirements = [requirement]
    current_req = None

    for sent in doc.sents:
        if "requirement" in sent.text.lower() or "shall" in sent.text.lower():  # Example rule to identify requirement start
            if current_req:
                requirements.append(current_req)
            current_req = {"requirement": sent.text, "description": ""}
        elif current_req:
            current_req["description"] += " " + sent.text

    # Add the last requirement
    if current_req:
        requirements.append(current_req)
    
    return requirements

# Function to save requirements to CSV
def save_to_csv(requirements, csv_path):
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Requirement", "Description"])
        for req in requirements:
            writer.writerow([req['requirement'], req['description']])

# Function to save requirements to JSON
def save_to_json(requirements, json_path):
    with open(json_path, 'w') as file:
        json.dump(requirements, file, indent=4)

# Main function
def main(pdf_path, csv_path, json_path):
    text = extract_text_from_pdf(pdf_path)
    ocr_text = extract_images_and_ocr(pdf_path)
    combined_text = text + ocr_text
    requirements = extract_requirements(combined_text)
    save_to_csv(requirements, csv_path)
    save_to_json(requirements, json_path)

# Example usage
pdf_path = "C:\\Users\\RITHWIK\\Downloads\\TechnicalSpecifications_Mobile_Surveillance_System_Item_3.pdf"
csv_path = 'requirements.csv'
json_path = 'requirements.json'
main(pdf_path, csv_path, json_path)
