import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import openai
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

# Function to extract requirements using LLM
def extract_requirements_with_llm(text):
    openai.api_key = 'your-openai-api-key'
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Extract all requirements and their descriptions from the following text:\n\n{text}"}
        ]
    )
    return response.choices[0].message['content']

# Function to parse extracted requirements from LLM response
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
def main(pdf_path, csv_path, json_path):
    text = extract_text_from_pdf(pdf_path)
    ocr_text = extract_images_and_ocr(pdf_path)
    combined_text = text + ocr_text
    llm_response = extract_requirements_with_llm(combined_text)
    requirements = parse_requirements(llm_response)
    save_to_csv(requirements, csv_path)
    save_to_json(requirements, json_path)

# Example usage
pdf_path = 'path/to/your/document.pdf'
csv_path = 'requirements.csv'
json_path = 'requirements.json'
main(pdf_path, csv_path, json_path)
