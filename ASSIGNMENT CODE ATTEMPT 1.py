from openai import OpenAI
import os

def generate_ai_response(topic):
    """
    Connects to the OpenAI API (GPT-3.5-turbo) to generate a short
    paragraph about a user-provided topic.
    """
    # The client automatically uses the OPENAI_API_KEY environment variable.
    try:
        client = OpenAI()
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        return None

    prompt = f"Write a single, simple, fun paragraph explaining why {topic} is interesting."

    # Generate a response using a fast model (gpt-3.5-turbo)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )

    return response.choices[0].message.content

# --- MAIN EXECUTION ---
if os.getenv("OPENAI_API_KEY") is None:
    print("\nERROR: The OPENAI_API_KEY environment variable is NOT set.")
    print("Please set your key in the terminal: export OPENAI_API_KEY='YOUR_KEY'")
else:
    user_topic = input("Enter a topic for the AI to explain (e.g., 'deep sea'): ")

    if user_topic:
        print(f"\nAI is generating an explanation for '{user_topic}'...")
        ai_text = generate_ai_response(user_topic)

        if ai_text:
            print("\n--- AI Explanation ---")
            print(ai_text)
            print("----------------------")
    else:
        print("No topic provided. Exiting.")