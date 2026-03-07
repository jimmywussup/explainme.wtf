import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents='What is the weather in Tokyo today?',
        config=types.GenerateContentConfig(
            tools=[{"google_search": {}}]
        )
    )
    print("SUCCESS: ", response.text)
except Exception as e:
    print("FAILED dict:", e)

try:
    response2 = client.models.generate_content(
        model='gemini-2.5-pro',
        contents='What is the weather in Tokyo today?',
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())]
        )
    )
    print("SUCCESS types.Tool: ", response2.text)
except Exception as e:
    print("FAILED types.Tool:", e)
