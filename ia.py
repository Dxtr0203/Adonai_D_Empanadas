from google import genai

client = genai.Client(api_key="AIzaSyA7MsTs9K6VZJVOpjdxPi5oY9snaO5fZ3c")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)