from .gemini import analyze_ingredients_with_gemini
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pytesseract
from PIL import Image
from .models import HarmfulIngredient  # Import the HarmfulIngredient model
import os
from django.core.files.base import ContentFile
import tempfile
from .gemini import generate_diet_plan_with_gemini
import datetime
import uuid

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

def diet_plan(request):
    if request.method == 'POST':
        try:
            details = {
                'age': request.POST.get('age'),
                'gender': request.POST.get('gender'),
                'height': request.POST.get('height'),
                'weight': request.POST.get('weight'),
                'activity_level': request.POST.get('activity_level'),
                'goal': request.POST.get('goal'),
            }
            # Basic validation
            if not all(details.values()):
                return JsonResponse({'error': 'Please fill out all fields.'}, status=400)
            
            plan = generate_diet_plan_with_gemini(details)

            # Store the plan in the session for calendar generation
            if 'error' not in plan:
                request.session['diet_plan_for_calendar'] = plan
                request.session.save()

            return JsonResponse(plan)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return render(request, 'diet_plan.html')

def generate_calendar(request):
    plan = request.session.get('diet_plan_for_calendar')

    if not plan or 'daily_plan' not in plan:
        return HttpResponse("No diet plan found in session. Please generate a plan first.", status=404)

    cal_name = "NutriScan Diet Plan"
    
    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        f"PRODID:-//NutriScan//AI Diet Plan v1.0//EN",
        f"NAME:{cal_name}",
        f"X-WR-CALNAME:{cal_name}",
        "CALSCALE:GREGORIAN",
    ]
    
    meal_times = {
        "breakfast": {"start": 8, "duration": 30},
        "lunch": {"start": 13, "duration": 30},
        "dinner": {"start": 19, "duration": 30},
        "snacks": {"start": 16, "duration": 15},
    }
    
    day_map = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5}
    rrule_map = {"monday": "MO", "tuesday": "TU", "wednesday": "WE", "thursday": "TH", "friday": "FR", "saturday": "SA"}

    today = datetime.date.today()
    
    for day_name, meals in plan['daily_plan'].items():
        day_name_lower = day_name.lower()
        if day_name_lower not in day_map:
            continue
            
        day_of_week = day_map[day_name_lower]
        days_ahead = day_of_week - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        
        next_occurrence_date = today + datetime.timedelta(days_ahead)

        for meal_name, description in meals.items():
            meal_name_lower = meal_name.lower()
            if meal_name_lower not in meal_times:
                continue

            start_hour = meal_times[meal_name_lower]['start']
            duration_minutes = meal_times[meal_name_lower]['duration']
            
            dtstart = datetime.datetime(
                next_occurrence_date.year, next_occurrence_date.month, next_occurrence_date.day,
                start_hour, 0, 0, tzinfo=datetime.timezone.utc
            )
            dtend = dtstart + datetime.timedelta(minutes=duration_minutes)
            
            # Properly escape characters for ICS file format
            escaped_description = description.replace(',', '\\,').replace(';', '\\;').replace('\n', '\\n')

            ics_content.extend([
                "BEGIN:VEVENT",
                f"UID:{uuid.uuid4()}@nutriscan.app",
                f"DTSTAMP:{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
                f"DTSTART:{dtstart.strftime('%Y%m%dT%H%M%SZ')}",
                f"DTEND:{dtend.strftime('%Y%m%dT%H%M%SZ')}",
                f"SUMMARY:{meal_name.capitalize()}: {description.split('.')[0]}",
                f"DESCRIPTION:{escaped_description}",
                f"RRULE:FREQ=WEEKLY;COUNT=2;BYDAY={rrule_map[day_name_lower]}",
                "END:VEVENT",
            ])

    ics_content.append("END:VCALENDAR")
    
    response_content = "\r\n".join(ics_content)
    response = HttpResponse(response_content, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="diet_plan.ics"'
    
    return response