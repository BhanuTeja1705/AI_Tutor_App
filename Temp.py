import google.generativeai as genai

genai.configure(api_key="AIzaSyC87IzT2bEwFsfXBLj77sKC14svyplOBMs")

models = genai.list_models()

for m in models:
    print(m)
