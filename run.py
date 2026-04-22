import requests
from tqdm import tqdm
from bs4 import BeautifulSoup
import os
import zipfile
import py7zr
import re
import time

DELAY_ENTRE_DOWNLOADS = 30  # segundos entre downloads normais
MAX_RETRIES = 5
WAIT_429 = 6000  # 60 minutos

def get_media(url):
    print(f"Obtendo info: {url}")
    response = requests.get(url, verify=False)

    if response.status_code != 200:
        print("Erro ao acessar página:", response.status_code)
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    media_id_element = soup.find('input', {'name': 'mediaId'})
    url_element = soup.find('form', {'id': 'dl_form'})

    if not media_id_element:
        print("Media não encontrada")
        return None

    return {
        'id': media_id_element['value'],
        'url': url_element['action']
    }


def download(media):
    download_url = "https:" + media['url'] + "?mediaId=" + media['id']

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://vimm.net/"
    }

    for tentativa in range(MAX_RETRIES):
        print(f"Tentativa {tentativa+1}: {download_url}")

        response = requests.get(download_url, headers=headers, stream=True, verify=False)

        if response.status_code == 200:
            total_size = int(response.headers.get('content-length', 0))
            content_disposition = response.headers.get('content-disposition', '')

            match = re.search(r'filename=\"(.+?)\"', content_disposition)
            filename = match.group(1) if match else f"file_{media['id']}"

            file_path = os.path.join("downloading", filename)
            os.makedirs("downloading", exist_ok=True)

            with tqdm(total=total_size, unit='B', unit_scale=True, desc=filename) as pbar:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            print("Download concluído!")
            extract_and_delete(file_path, "finished")
            return

        elif response.status_code == 429:
            print(f"Rate limit (429). Aguardando {WAIT_429/60:.0f} minutos...")
            time.sleep(WAIT_429)

        else:
            print("Erro:", response.status_code)
            return

    print("Falhou após várias tentativas.")


def extract_and_delete(archive_path, extract_dir):
    try:
        os.makedirs(extract_dir, exist_ok=True)

        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

        elif archive_path.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, 'r') as seven_zip:
                seven_zip.extractall(extract_dir)

        else:
            print("Formato não suportado")
            return False

        os.remove(archive_path)
        return True

    except Exception as e:
        print("Erro ao extrair:", e)
        return False


def download_from_txt(file):
    with open(file, 'r') as f:
        for line in f:
            url = line.strip()
            if not url:
                continue

            media = get_media(url)

            if media:
                download(media)
                print(f"Aguardando {DELAY_ENTRE_DOWNLOADS}s...\n")
                time.sleep(DELAY_ENTRE_DOWNLOADS)
            else:
                print("Pulando URL inválida\n")


if __name__ == "__main__":
    download_from_txt("links.txt")
