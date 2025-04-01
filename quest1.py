import requests
from bs4 import BeautifulSoup
import os
import zipfile
import wget
import hashlib
from urllib.parse import urljoin

def download_anexos(url):
   
    try:
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
      
        response = requests.get(url, headers=headers)
        response.raise_for_status()  

        soup = BeautifulSoup(response.content, 'html.parser')
        
        
        pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))
        
        
        if not pdf_links:
            print(f"Nenhum PDF encontrado na URL: {url}")
            return False
        
        
        os.makedirs('anexos', exist_ok=True)
        
        
        downloaded_files = []
        skipped_files = []
        
        for link in pdf_links:
            pdf_url = link.get('href')
            
            
            pdf_url = urljoin(url, pdf_url)
            
            filename = os.path.join('anexos', pdf_url.split('/')[-1])
            
            
            if os.path.exists(filename):
                print(f"\nArquivo já existe, pulando download: {filename}")
                skipped_files.append(filename)
                continue
            
            try:
                print(f"\nBaixando: {os.path.basename(filename)}")
                wget.download(pdf_url, filename)
                downloaded_files.append(filename)
                print(f" - Concluído!")
            except Exception as download_error:
                print(f"\nErro ao baixar {pdf_url}: {download_error}")
        
        
        files_to_zip = downloaded_files + skipped_files
        
        
        if not files_to_zip:
            print("Nenhum arquivo disponível para compactação.")
            return False
        
        need_to_zip = True
        if os.path.exists('anexos.zip') and not downloaded_files:
            print("Nenhum novo arquivo foi baixado, mantendo o arquivo ZIP existente.")
            need_to_zip = False
        
      
        if need_to_zip:
            print("\nCompactando arquivos...")
            with zipfile.ZipFile('anexos.zip', 'w') as zipf:
                for file in files_to_zip:
                    zipf.write(file, os.path.basename(file))
            print("Compactação concluída!")
        
        if downloaded_files:
            print(f"\nArquivos baixados nesta execução: {len(downloaded_files)}")
        if skipped_files:
            print(f"Arquivos que já existiam: {len(skipped_files)}")
        
        print("\nProcesso concluído com sucesso!")
        return True
        
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP: {http_err}")
        return False
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erro de conexão: {conn_err}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False


url = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
success = download_anexos(url)

if not success:
    print("Processo de download e compactação não foi concluído com sucesso.")