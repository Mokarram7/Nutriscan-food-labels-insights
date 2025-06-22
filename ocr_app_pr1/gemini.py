import google.generativeai as genai
import json

# Directly configure Gemini with your API key
genai.configure(api_key="AIzaSyB2xh0evZ_-s_nBoZF_qjD-ChDl4PPnlVg")

def analyze_ingredients_with_gemini(ingredients_text):
    prompt = f"""
    You are a food safety expert. Based on the following ingredients list, provide a detailed analysis in JSON format.

    Ingredients:
    "{ingredients_text}"

    Please structure your response as a JSON object with the following keys:
    - "health_score": An integer from 1 to 10 (1=very unhealthy, 10=very healthy).
    - "summary": A one-sentence summary of the product's healthiness.
    - "harmful_ingredients": A list of potentially harmful or ultra-processed ingredients found, with a brief explanation for each as a list of objects with "name" and "reason" keys.
    - "health_concerns": A list of strings detailing potential health concerns (e.g., "High in sodium, may affect blood pressure.").
    - "alternatives": A short paragraph suggesting healthier alternatives.

    Example of expected output:
    {{
        "health_score": 3,
        "summary": "This product is high in processed ingredients and sugar.",
        "harmful_ingredients": [
            {{"name": "High Fructose Corn Syrup", "reason": "Linked to obesity and metabolic issues."}},
            {{"name": "Artificial Colors", "reason": "Some colors are linked to hyperactivity in children."}}
        ],
        "health_concerns": [
            "Not suitable for diabetics due to high sugar content.",
            "Contains ingredients that may cause allergic reactions in sensitive individuals."
        ],
        "alternatives": "Consider looking for snacks made with whole grains and natural sweeteners like fruit or stevia. Products with shorter, more recognizable ingredient lists are generally a better choice."
    }}

    Provide only the JSON object in your response.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)
        
        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        return json.loads(text_response)
    except Exception as e:
        return {
            "error": f"An error occurred during Gemini analysis: {str(e)}",
            "details": "Could not parse the analysis from the AI model. The model may have returned an unexpected format."
        }

def generate_diet_plan_with_gemini(details):
    prompt = f"""
    You are a professional nutritionist and fitness coach. Based on the following user details, create a 6-day personalized diet plan (Monday to Saturday) in JSON format.

    User Details:
    - Age: {details.get('age')}
    - Gender: {details.get('gender')}
    - Height: {details.get('height')} cm
    - Weight: {details.get('weight')} kg
    - Activity Level: {details.get('activity_level', 'Not specified').replace('_', ' ')}
    - Primary Goal: {details.get('goal', 'Not specified').replace('_', ' ')}

    Please structure your response as a JSON object with the following keys:
    - "summary": A brief, encouraging summary (2-3 sentences) of the diet plan's strategy, including estimated daily calorie intake.
    - "daily_plan": An object containing keys for each day from "monday" to "saturday". Each day should be an object with keys for "breakfast", "lunch", "dinner", and "snacks".

    Example of expected output:
    {{
      "summary": "This 6-day plan focuses on lean proteins, complex carbs, and healthy fats to support your goal of weight loss. Expect a daily intake of around 1800-2000 calories. Stay hydrated and remember consistency is key! Sunday is a rest day.",
      "daily_plan": {{
        "monday": {{
          "breakfast": "Scrambled eggs (2) with spinach and a slice of whole-wheat toast.",
          "lunch": "Grilled chicken salad with mixed greens, cherry tomatoes, cucumbers, and a light vinaigrette.",
          "dinner": "Baked salmon with a side of quinoa and roasted asparagus.",
          "snacks": "A handful of almonds and a Greek yogurt."
        }},
        "tuesday": {{
          "breakfast": "Oatmeal with berries and a sprinkle of chia seeds.",
          "lunch": "Leftover baked salmon and quinoa.",
          "dinner": "Lean turkey meatballs with zucchini noodles and marinara sauce.",
          "snacks": "An apple with a tablespoon of peanut butter."
        }}
      }}
    }}

    Provide only the JSON object in your response.
    """
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        text_response = response.text.strip()
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]

        return json.loads(text_response)
    except Exception as e:
        return {
            "error": f"An error occurred during Gemini analysis: {str(e)}"
        }
