# This script connects to the Gemini API to generate an explanation
# for a user-provided topic and saves the response to a file.

import os
import json
import requests
import sys

# The API key is automatically provided in the environment.
# We do not need to set it manually.
API_KEY = "AIzaSyDHLgMqeD8vvKmOVPfYPszGfx7rVE6CY98"
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key="

def generate_ai_response(topic):
    """
    Connects to the Gemini API to generate a short paragraph about a user-provided topic.
    """
    prompt = f"Write a single, simple, fun paragraph explaining why {topic} is interesting."

    # Construct the payload for the API request
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Use requests to send the payload to the Gemini API
        response = requests.post(f"{API_URL}{API_KEY}", headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # This will raise an HTTPError if the response was an error
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the generated text from the response
        if 'candidates' in data and len(data['candidates']) > 0:
            text = data['candidates'][0]['content']['parts'][0]['text']
            return text
        else:
            return "No explanation could be generated."

    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Unexpected API response structure: {e}")
        return "An error occurred while parsing the AI's response."

def save_response_to_file(topic, text):
    """
    Saves the generated AI text to a text file.
    The filename is based on the topic.
    """
    filename = f"{topic.replace(' ', '_').lower()}_explanation.txt"
    with open(filename, "w", encoding='utf-8') as file:
        file.write(text)
    print(f"Explanation saved to {filename}")

# --- MAIN EXECUTION ---
user_topic = input("Enter a topic for the AI to explain (e.g., 'deep sea'): ")

if user_topic:
    print(f"\nAI is generating an explanation for '{user_topic}'...")
    ai_text = generate_ai_response(user_topic)

    if ai_text:
        print("\n--- AI Explanation ---")
        print(ai_text)
        print("----------------------")
        save_response_to_file(user_topic, ai_text)
else:
    print("No topic provided. Exiting.")
