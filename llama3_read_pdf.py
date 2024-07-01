import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import requests
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

# Function to extract requirements using LLaMA 3
def extract_requirements_with_llama(text, llama_api_url, llama_api_key):
    headers = {
        'Authorization': f'Bearer {llama_api_key}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'llama-3',
        'prompt': f"Extract all requirements and their descriptions from the following text:\n\n{text}",
        'max_tokens': 1000
    }
    response = requests.post(llama_api_url, headers=headers, json=payload)
    return response.json()['choices'][0]['text']

# Function to parse extracted requirements from LLaMA 3 response
def parse_requirements(llm_response):
    requirements = []
    for line in llm_response.split("\n"):
        if line.strip():
            parts = line.split(": ", 1)
            if len(parts) == 2:
                requirement, description = parts
                requirements.append({"requirement": requirement.strip(), "description": description.strip()})
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
def main(pdf_path, csv_path, json_path, llama_api_url, llama_api_key):
    text = extract_text_from_pdf(pdf_path)
    ocr_text = extract_images_and_ocr(pdf_path)
    combined_text = text + ocr_text
    llm_response = extract_requirements_with_llama(combined_text, llama_api_url, llama_api_key)
    requirements = parse_requirements(llm_response)
    save_to_csv(requirements, csv_path)
    save_to_json(requirements, json_path)

# Example usage
pdf_path = 'path/to/your/document.pdf'
csv_path = 'requirements.csv'
json_path = 'requirements.json'
llama_api_url = 'https://api.your-llama-provider.com/v1/completions'
llama_api_key = 'your-llama-api-key'
main(pdf_path, csv_path, json_path, llama_api_url, llama_api_key)
