import os
import io
import httpx
import pathlib
from PyPDF2 import PdfReader, PdfWriter
from google import genai
from google.genai import types
from dotenv import load_dotenv
from db.database import supabase
load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generate_text(prompt, model="gemini-2.5-flash"):
    """Generate text using Google GenAI"""
    response = client.models.generate_content(
        model=model,
        contents=[types.Part.from_text(prompt)]
    )
    return response.text

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

def compress_pdf(input_buffer):
    """Kompresi PDF untuk mengurangi ukuran file"""
    reader = PdfReader(input_buffer)
    writer = PdfWriter()

    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)

    output_buffer = io.BytesIO()
    writer.write(output_buffer)
    output_buffer.seek(0)
    return output_buffer

def upload_to_supabase_storage(file_buffer, file_name):
    """Upload file ke Supabase Storage"""
    try:
        # Upload file dengan content type PDF
        supabase.storage.from_(os.getenv("SUPABASE_BUCKET")).upload(
            file=file_buffer.getvalue(),
            path=file_name,
            file_options={
                "content-type": "application/pdf"
            }
        )

        public_url = supabase.storage.from_(os.getenv("SUPABASE_BUCKET")).get_public_url(file_name)
        return public_url

    except Exception as e:
        print(f"Error uploading to Supabase Storage: {e}")
        return None

def convert_date(date):
  # Mapping bulan dari Indonesia ke Inggris
  month_mapping = {
    "Januari": "January", "Februari": "February", "Maret": "March",
    "April": "April", "Mei": "May", "Juni": "June",
    "Juli": "July", "Agustus": "August", "September": "September",
    "Oktober": "October", "Nopember": "November", "Desember": "December"
  }

  return month_mapping.get(date, date) if date else None
