import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import spacy
import csv
import json

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Function to extract images from PDF and perform OCR
def extract_images_and_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_text = ""
    for page_num in range(len(doc)):
        for img in doc.get_page_images(page_num):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            ocr_text += pytesseract.image_to_string(image)
    return ocr_text

# Function to extract requirements using NLP
def extract_requirements(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    requirements = []
    current_req = None

    for sent in doc.sents:
        if "requirement" in sent.text.lower():  # Simple rule to identify requirement start
            if current_req:
                requirements.append(current_req)
            current_req = {"requirement": sent.text, "description": ""}
        elif current_req:
            current_req["description"] += sent.text

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
pdf_path = 'path/to/your/document.pdf'
csv_path = 'requirements.csv'
json_path = 'requirements.json'
main(pdf_path, csv_path, json_path)
