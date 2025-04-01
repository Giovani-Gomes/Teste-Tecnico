import requests
from bs4 import BeautifulSoup
import os
import zipfile
import wget

def download_anexos():
   
    url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-pocedimentos"
    
    try:
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
      
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))
        
      
        os.makedirs('anexos', exist_ok=True)
        
       
        downloaded_files = []
        for link in pdf_links:
            pdf_url = link.get('href')
            filename = os.path.join('anexos', pdf_url.split('/')[-1])
            wget.download(pdf_url, filename)
            downloaded_files.append(filename)
        
      
        with zipfile.ZipFile('anexos.zip', 'w') as zipf:
            for file in downloaded_files:
                zipf.write(file, os.path.basename(file))
        
        print("Download e compactação concluídos com sucesso!")
        
    except Exception as e:
        print(f"Erro no download: {e}")

download_anexos()

