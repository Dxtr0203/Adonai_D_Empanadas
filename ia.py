from google import genai

client = genai.Client(api_key="AIzaSyAvIvQpRW6qL3ZqWtU8LY1o_RJjTeFrucs")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain how AI works in a few words"
)
print(response.text)