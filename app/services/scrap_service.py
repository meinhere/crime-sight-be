import requests
import io
import os
import uuid
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
from itertools import zip_longest
from ..dependencies import extract_url_document, compress_pdf, upload_to_supabase_storage, convert_date
from ..db.database import supabase

prompt_detail_putusan = """
Saya memiliki dokumen putusan pengadilan pidana dan ingin Anda merangkum isinya dalam format berikut.
{
  "alamat_kejadian": <berisi alamat atau tempat kejadian perkara dengan format dusun (tanpa rt rw), desa, kecamatan, kabupaten, provinsi>
  "status_tahanan": <berisi status tahanan terdakwa saat ini>,
  "lama_tahanan": <berisi lama tahanan terdakwa dalam format tahun dan bulan, contohnya: 1 tahun dan 2 bulan (jka tidak ada tahun tampilkan bulan saja)>,
  "barang_bukti": <berisi barang bukti yang ditemukan secara singkat, disebutkan jumlah dan merk (jika ada), dan tidak perlu disebutkan ciri-cirinya, jika lebih dari 1 barang bukti pisahkan dengan tanda ','>,
  "hasil_putusan": <berisi hasil putusan sidang yang telah dilakukan>,
  "hakim": [
    {
      "nama_hakim": <berisi nama hakim>,
      "jabatan": <berisi nama jabatan hakim>
    },
    ...
  ],
  "terdakwa": [
    {
      "nama_lengkap": <berisi nama lengkap terdakwa>,
      "jenis_kelamin": <berisi nama jenis_kelamin terdakwa (Laki-Laki atau Perempuan)>,
      "alamat": <berisi alamat terdakwa>,
      "tempat_lahir": <berisi tempat lahir terdakwa>,
      "pekerjaan": <berisi pekerjaan terdakwa>,
      "umur": <berisi umur terdakwa (hanya angka)>,
      "kebangsaan": <berisi kebangsaan terdakwa>,
      "agama": <berisi agama terdakwa>,
    },
    ...
  ],
  "penasihat": [
    {
      "nama_penasihat": <berisi nama penasihat>
    },
    ...
  ],
  "penuntut_umum": [
    {
      "nama_penuntut": <berisi nama penuntut>
    },
    ...
  ],
  "saksi": [
    {
      "nama_saksi": <berisi nama saksi>
    },
    ...
  ],
  "lokasi_kejadian_id": <berdasarkan hasil pembacaan dokumen dan memilih salah satu dari pilihan berikut secara tepat: 'Rumah', 'Jalan Umum', 'Perkantoran', 'Pertokoan/Mal/Pusat Perbelanjaan', 'Pasar', 'Persawahan', 'Tempat Parkir', 'Pergudangan', 'SPBU', 'Bank', 'Perairan', 'Pertambangan'>,
  "waktu_kejadian_id": <berdasarkan hasil pembacaan dokumen dan memilih salah satu dari pilihan berikut secara tepat: 'Pagi (06:00 - 11:59)', 'Siang (12:00 - 15:59)', S'ore (16:00 - 18:59)', 'Malam (19:00 - 23:59)', 'Dini Hari (00:00 - 05:59)', 'Tidak Diketahui'>,
  "kode_kabupaten": <berdasarkan hasil pembacaan dokumen untuk melihat kode dari kabupaten atau kota di indonesia (tanpa tambahan tanda baca) contohnya: '3528'>
}
"""

def save_putusan_detail(data, table_name):
    """Simpan format data detail putusan"""
    column_names = {
        'hakim': 'nama_hakim',
        'terdakwa': 'nama_lengkap',
        'penasihat': 'nama_penasihat',
        'penuntut_umum': 'nama_penuntut',
        'saksi': 'nama_saksi'
    }
    column_name = column_names.table_name
    
    try:
        for idx, table in enumerate(data):
          data_existing = supabase.table(table_name).select('id').eq(column_name, table[column_name]).execute()
          if len(data_existing.data) == 0:
            table['id'] = str(uuid.uuid4())
            table['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            res = supabase.table(table_name).insert(table).execute()
            id = res.data[0]['id']
          else:
            id = data_existing.data[0]['id']

          data[idx]['id'] = id

    except Exception as e:
        print(f"Error saat menyimpan putusan: {e}")
        return None

def get_all_links(base_url, page=1, page_end=None):
    """Ambil semua link putusan dari semua halaman"""
    links = []
    while True:
        # Cek jika halaman melebihi batas
        if (page and page_end) and page > page_end:
            break

        url = f"{base_url}/page/{page}.html" if page > 1 else base_url
        print(f"Mengambil halaman {page}...")

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Cek jika sudah di halaman terakhir
            if "Tidak ditemukan" in soup.text:
                break

            # Ambil semua link putusan
            items = soup.select('.spost.clearfix .entry-c strong a')
            if not items:
                break

            for item in items:
                # Cek jika judul putusan (pid.c -> banyak data yg tidak lengkap)
                if "pid.c" not in item.text.lower():
                  links.append(urljoin(base_url, item['href']))

            page += 1
            time.sleep(1)  # Delay untuk menghindari blocking

        except Exception as e:
            print(f"Error saat mengambil halaman {page}: {e}")
            break

    return links

def extract_putusan_data(url):
    """Ekstrak data putusan dari halaman detail"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Cek apakah ada PDF
        pdf_link = None
        pdf_btn = soup.select_one('a[href*="/pdf/"]')
        if pdf_btn:
            pdf_link = urljoin(url, pdf_btn['href'])
        else:
          return None

        # Ekstrak metadata
        data = {
            "nomor_putusan": None,
            "uri_dokumen": pdf_link,
            "judul_putusan": None,
            "tahun": None,
            "lembaga_peradilan": None,
            "panitera": None,
            "jenis_kejahatan": None,
            "lokasi_kejadian_id": None,
            "waktu_kejadian_id": None,
            "tanggal_upload": None,
            "tanggal_musyawarah": None,
            "tanggal_dibacakan": None,
            "vonis_hukuman": None,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Format data dari scraping ke kolom table
        format_data = {
            "nomor": "nomor_putusan",
            "kata_kunci": "jenis_kejahatan",
            "tanggal_register": "tanggal_upload",
            "amar_lainnya": "vonis_hukuman"
        }

        # Ekstrak data dari tabel
        rows = soup.select('.table tr')
        for row in rows:
            cols = row.find_all('td')

            if len(cols) == 1:
              value = cols[0].find('strong').text.strip()
              if value:
                data['judul_putusan'] = value
            elif len(cols) == 2:
                key = cols[0].text.strip().lower().replace(" ", "_")
                value = cols[1].text.strip()

                if key in format_data:
                    key = format_data[key]

                if key in ['tanggal_upload', 'tanggal_musyawarah', 'tanggal_dibacakan']:
                    value = convert_date(value)

                if key in data:
                    data[key] = value

        return data

    except Exception as e:
        print(f"Error saat ekstrak data dari {url}: {e}")
        return None
    
def process_putusan(putusan_url):
    """Proses satu putusan: ekstrak data + simpan PDF"""
    try:
        # Ekstrak metadata
        data = extract_putusan_data(putusan_url)
        if not data:
            print(f"Gagal memproses {putusan_url} karena tidak memiliki link dokumen, dilewati...")
            return True

        # Ekstrak data detail
        data_detail = {
            "alamat_kejadian": None,
            "status_tahanan": None,
            "lama_tahanan": None,
            "barang_bukti": None,
            "hasil_putusan": None,
            "lokasi_kejadian_id": None,
            "waktu_kejadian_id": None,
            "kode_kabupaten": None,
            "hakim": [],
            "terdakwa": [],
            "penasihat": [],
            "penuntut_umum": [],
            "saksi": []
        }

        # Cek apakah sudah ada di database
        existing_data = supabase.table('putusan').select('id').eq('nomor_putusan', data['nomor_putusan']).execute()
        if existing_data.data:
            print(f"Putusan {data['nomor_putusan']} sudah ada, dilewati...")
            return True

        # Download PDF
        pdf_response = requests.get(data['uri_dokumen'])
        pdf_response.raise_for_status()
        pdf_buffer = io.BytesIO(pdf_response.content)

        # Kompres PDF
        compressed_pdf = compress_pdf(pdf_buffer)

        # Upload ke Supabase Storage
        format_file_name = data['nomor_putusan'].strip().replace(" ", "_").replace("/", "_")
        file_name = f"putusan/{format_file_name}.pdf"

        # Cek apakah sudah ada data di storage
        existing_data = supabase.storage.from_(os.getenv("SUPABASE_BUCKET")).list('putusan', {"limit": 1, "search": format_file_name})
        if existing_data:
          print(f"File {file_name} sudah ada di storage, dilewati...")
          return None

        public_url = upload_to_supabase_storage(compressed_pdf, file_name)

        if public_url:
            # Update data dengan URL Supabase
            data['uri_dokumen'] = public_url

            # Data ekstrak dokumen
            result_extract_document = extract_url_document(prompt_detail_putusan, public_url).strip()[7:-3]
            detail_document = json.loads(result_extract_document)

            # Ambil data waktu dan lokasi kejadian
            data_waktu_kejadian = supabase.table('waktu_kejadian').select('id', 'waktu_kejadian').execute().data
            data_lokasi_kejadian = supabase.table('lokasi_kejadian').select('id', 'nama_lokasi').execute().data
            waktu_kejadian_default = '5179ef1c-aaba-46d8-81eb-c4e5594a2a6f' # id dari data 'Tidak Diketahui' pada database
            lokasi_kejadian_default = 'd6681071-1eb0-4995-b33e-de78fd87e7c1' # id dari data 'Jalan Umum' pada database

            # Isi data detail
            for key in detail_document:
              if key == 'waktu_kejadian_id':
                id_waktu_kejadian = next((item['id'] for item in data_waktu_kejadian if item['waktu_kejadian'] == detail_document['waktu_kejadian_id']), waktu_kejadian_default)
                detail_document['waktu_kejadian_id'] = id_waktu_kejadian
              elif key == 'lokasi_kejadian_id':
                id_lokasi_kejadian = next((item['id'] for item in data_lokasi_kejadian if item['nama_lokasi'] == detail_document['lokasi_kejadian_id']), lokasi_kejadian_default)
                detail_document['lokasi_kejadian_id'] = id_lokasi_kejadian

              if key in data_detail:
                data_detail[key] = detail_document[key]

            # Kelola data untuk simpan ke db
            data.update(data_detail)
            data_putusan = dict(list(data.items())[:-5])
            data_hakim = data['hakim']
            data_terdakwa = data['terdakwa']
            data_penasihat = data['penasihat']
            data_penuntut_umum = data['penuntut_umum']
            data_saksi = data['saksi']

            # Simpan data putusan
            data_putusan['id'] = str(uuid.uuid4())
            res = supabase.table('putusan').insert(data_putusan).execute()
            nomor_putusan = res.data[0]['nomor_putusan']

            # Simpan data detail
            save_putusan_detail(data_hakim, 'hakim')
            save_putusan_detail(data_terdakwa, 'terdakwa')
            save_putusan_detail(data_penasihat, 'penasihat')
            save_putusan_detail(data_penuntut_umum, 'penuntut_umum')
            save_putusan_detail(data_saksi, 'saksi')

            # Gabung data putusan detail
            data_putusan_detail = []
            for hakim, terdakwa, penasihat, penuntut, saksi in zip_longest(
                data_hakim,
                data_terdakwa,
                data_penasihat,
                data_penuntut_umum,
                data_saksi,
                fillvalue={}
            ):
                data_putusan_detail.append({
                    'id': str(uuid.uuid4()),
                    'nomor_putusan': nomor_putusan,
                    'hakim_id': hakim.get('id') if hakim else None,
                    'terdakwa_id': terdakwa.get('id') if terdakwa else None,
                    'penasihat_id': penasihat.get('id') if penasihat else None,
                    'penuntut_umum_id': penuntut.get('id') if penuntut else None,
                    'saksi_id': saksi.get('id') if saksi else None,
                    'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

            # Simpan data putusan detail
            for detail in data_putusan_detail:
              supabase.table('putusan_detail').insert(detail).execute()

            print(f"Berhasil menyimpan putusan {data['nomor_putusan']}")
            return True

        return False

    except Exception as e:
        print(f"Error memproses {putusan_url}: {e}")
        return False