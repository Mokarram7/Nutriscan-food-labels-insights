from .gemini import analyze_ingredients_with_gemini
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pytesseract
from PIL import Image
from .models import HarmfulIngredient  # Import the HarmfulIngredient model
import os
from django.core.files.base import ContentFile
import tempfile

# Set the Tesseract OCR path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
import shutil
tesseract_cmd = shutil.which("tesseract")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    raise RuntimeError("Tesseract OCR not found!")


def upload_and_scan_image(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        file_name = uploaded_file.name
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name
        temp_file.close()

        try:
            # Perform OCR processing on the image
            with open(temp_file_path, 'rb') as image_file:
                extracted_text = pytesseract.image_to_string(Image.open(image_file))

            # Get all harmful ingredients from the database
            harmful_ingredients = HarmfulIngredient.objects.all()
            matched_ingredients = []

            # Check for matches in the extracted text
            for ingredient in harmful_ingredients:
                if ingredient.name.lower() in extracted_text.lower():
                    matched_ingredients.append({
                        'name': ingredient.name,
                        'description': ingredient.description
                    })

            # 🔥 Call Gemini to analyze full OCR text
            gemini_analysis = analyze_ingredients_with_gemini(extracted_text)
            
            # Store results in session
            request.session['analysis_results'] = {
                'matched_ingredients': matched_ingredients,
                'gemini_analysis': gemini_analysis,
            }
            request.session.save()

            # Return a success response that JS will use to redirect
            return JsonResponse({'status': 'success', 'redirect_url': '/Ingredient'})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'index.html')

def About(request):
    return render(request, 'About.html')
def Contact(request):
    return render(request, 'Contact.html')
def Home(request):
    return render (request, 'Home.html')
def Ingredient(request):
    results = request.session.pop('analysis_results', None)
    return render (request, 'Ingredient.html', {'results': results})