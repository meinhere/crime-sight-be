from google import genai
from google.genai import types
import os
import httpx
import pathlib
from dotenv import load_dotenv
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def extract_url_document(prompt, doc_url, model="gemini-2.5-flash"):
  """Ekstrak data dokumen putusan dari public storage supabase"""
  doc_data = httpx.get(doc_url).content

  response = client.models.generate_content(
    model=model,
    contents=[
        types.Part.from_bytes(
          data=doc_data,
          mime_type='application/pdf',
        ),
        prompt])

  return response.text

def extract_local_document(prompt, filename, model="gemini-2.5-flash"):
  """Ekstrak data dokumen putusan dari local storage"""
  filepath = pathlib.Path(filename)

  response = client.models.generate_content(
    model=model,
    contents=[
        types.Part.from_bytes(
          data=filepath.read_bytes(),
          mime_type='application/pdf',
        ),
        prompt])
  return response.text
