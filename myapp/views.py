from django.shortcuts import render
import pytesseract
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

from django.shortcuts import render
from .forms import AadharImageForm
import cv2

import re
import io
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile

def get_front_values(text):
    regex_name = None
    regex_gender = None
    regex_dob = None
    regex_aadhaar_number = None

    # Extracting name
    name_entities = re.findall(r"[A-Z][a-z]+", text)
    if name_entities:
        # Join the first two words (usually first name and middle name)
        regex_name = ' '.join(name_entities[3:5])

    # Extracting gender
    gender_entities = re.findall(r"MALE|FEMALE|male|female|Male|Female", text)
    if gender_entities:
        regex_gender = gender_entities[0].upper()

    # Extracting date of birth
    dob_entities = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    if dob_entities:
        regex_dob = dob_entities[0]

    # Extracting Aadhaar number
    aadhaar_entities = re.findall(r"\d{4} \d{4} \d{4}", text)
    if aadhaar_entities:
        regex_aadhaar_number = aadhaar_entities[0]

    return regex_name, regex_gender, regex_dob, regex_aadhaar_number

def get_back_values(text):
    regex_address = None

    # Extracting address
    address_entities = re.findall(r"Address\s[A-Z][a-z]+", text, re.DOTALL)
    if address_entities:
        regex_address = address_entities[0].strip()

    return regex_address

def extract_info(front_image, back_image):
    # Convert the images to grayscale
    front_gray = cv2.cvtColor(front_image, cv2.COLOR_BGR2GRAY)
    back_gray = cv2.cvtColor(back_image, cv2.COLOR_BGR2GRAY)

    # Perform OCR on the images to extract text
    front_text = pytesseract.image_to_string(front_gray, lang='eng')
    back_text = pytesseract.image_to_string(back_gray, lang='eng')

    # Extract information from the front image
    name, gender, dob, aadhaar_number = get_front_values(front_text)

    # Extract information from the back image
    address = get_back_values(back_text)

    return name, gender, dob, aadhaar_number, address

def upload_aadhar(request):
    error_message = None

    if request.method == 'POST':
        form = AadharImageForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded images temporarily
            front_image_file = request.FILES['front_image']
            back_image_file = request.FILES['back_image']

            # Create InMemoryUploadedFile instances
            front_image = InMemoryUploadedFile(front_image_file, None, 'temp_front_image.jpg',
                                                'image/jpeg', front_image_file.tell(), None)
            back_image = InMemoryUploadedFile(back_image_file, None, 'temp_back_image.jpg',
                                               'image/jpeg', back_image_file.tell(), None)

            # Read the uploaded images with error handling
            try:
                front_image_data = io.BytesIO(front_image.read())
                back_image_data = io.BytesIO(back_image.read())

                front_image = cv2.imdecode(np.frombuffer(front_image_data.read(), np.uint8), cv2.IMREAD_COLOR)
                back_image = cv2.imdecode(np.frombuffer(back_image_data.read(), np.uint8), cv2.IMREAD_COLOR)
            except Exception as e:
                # Handle the error
                error_message = str(e)
                return render(request, 'aadhar_upload.html', {'form': form, 'error_message': error_message})

            # Extract information from the images
            try:
                name, gender, dob, aadhaar_number, address = extract_info(front_image, back_image)
            except Exception as e:
                # Handle the error
                error_message = str(e)
                return render(request, 'aadhar_upload.html', {'form': form, 'error_message': error_message})

            # Pass extracted information in the context
            context = {
                'name': name,
                'gender': gender,
                'dob': dob,
                'aadhaar_number': aadhaar_number,
                'address': address
            }

            # Render the result template with extracted information
            return render(request, 'aadhar_result.html', context)
    else:
        form = AadharImageForm()
    return render(request, 'aadhar_upload.html', {'form': form, 'error_message': error_message})

def view_result(request):
    # Assuming you have a template named 'aadhar_result.html' for displaying the result
    return render(request, 'aadhar_result.html')

# Create your views here.
