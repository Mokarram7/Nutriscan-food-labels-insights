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
