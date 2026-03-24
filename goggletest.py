import google.generativeai as genai

genai.configure(api_key="AIzaSyBb6vXKvnYeXyAekQGWP9p0KXv7GBAPa2c")

for m in genai.list_models():
    print(m.name)