import pdfplumber
import pandas as pd
import zipfile
import os
import logging
from datetime import datetime
import glob
import sys
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("LOGS.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

NOME = "Giovani_Gomes"
ARQUIVO = "Anexo_I_Rol_2021RN_465.2021_RN627L.2024.pdf"

def encontrar_pdf(nome_arquivo=ARQUIVO, diretorio=None):
 
    diretorios_busca = []
    
   
    if diretorio and os.path.isdir(diretorio):
        diretorios_busca.append(diretorio)
    
    
    diretorios_busca.append(os.getcwd())
    
   
    diretorios_busca.append(os.path.join(os.getcwd(), 'anexos'))
   
    diretorios_busca.append(os.path.dirname(os.path.abspath(__file__)))
    
   
    diretorios_busca.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anexos'))
    
    
    home_dir = str(Path.home())
    diretorios_busca.append(home_dir)
    diretorios_busca.append(os.path.join(home_dir, 'anexos'))
    diretorios_busca.append(os.path.join(home_dir, 'meu_projeto_flask', 'anexos'))
    
   
    diretorios_busca.append(os.path.join(home_dir, 'Downloads'))
    diretorios_busca.append(os.path.join(home_dir, 'Documentos'))
    diretorios_busca.append(os.path.join(home_dir, 'Documents'))
    
    logger.info(f"Buscando arquivo específico '{nome_arquivo}' em {len(diretorios_busca)} diretórios")
    
  
    for dir_path in diretorios_busca:
        if not os.path.exists(dir_path):
            continue
            
        caminho_completo = os.path.join(dir_path, nome_arquivo)
        if os.path.isfile(caminho_completo):
            logger.info(f"Arquivo alvo encontrado: {caminho_completo}")
            return caminho_completo
    
    logger.warning(f"Arquivo específico '{nome_arquivo}' não encontrado. Buscando alternativas...")
    
   
    padroes_busca = [
        'Anexo_I*.pdf',
        'anexo_i*.pdf', 
        'Anexo*.pdf', 
        'anexo*.pdf',
        'Rol*.pdf',
        '*.pdf'
    ]
    
    for dir_path in diretorios_busca:
        if not os.path.exists(dir_path):
            continue
            
        for padrao in padroes_busca:
            arquivos = glob.glob(os.path.join(dir_path, padrao))
            if arquivos:
                logger.info(f"Arquivo alternativo encontrado: {arquivos[0]}")
                return arquivos[0]
    
    logger.error("Nenhum arquivo PDF encontrado nos diretórios de busca.")
    return None

def obter_diretorio_saida():
  
   
    diretorios_possiveis = [
        os.getcwd(),  
        os.path.join(os.getcwd(), 'resultados'),  
        str(Path.home()),  
        os.path.join(str(Path.home()), 'resultados'),  
        os.path.dirname(os.path.abspath(__file__))  
    ]
    
    for diretorio in diretorios_possiveis:
        
        if not os.path.exists(diretorio):
            try:
                os.makedirs(diretorio)
                logger.info(f"Diretório criado: {diretorio}")
            except:
                continue
        
        
        if os.access(diretorio, os.W_OK):
            logger.info(f"Usando diretório de saída: {diretorio}")
            return diretorio
    
    
    import tempfile
    temp_dir = tempfile.gettempdir()
    logger.warning(f"Usando diretório temporário para salvar: {temp_dir}")
    return temp_dir

def verificar_arquivo_existe(arquivo):
   
    existe = os.path.isfile(arquivo)
    if existe:
        logger.info(f"Arquivo {arquivo} já existe.")
    return existe

def extrair_tabela_do_pdf(pdf_path):
   
    if not os.path.exists(pdf_path):
        logger.error(f"Arquivo PDF não encontrado: {pdf_path}")
        return None
    
    logger.info(f"Iniciando extração de tabelas do arquivo: {pdf_path}")
    data = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_paginas = len(pdf.pages)
            logger.info(f"Total de páginas no PDF: {total_paginas}")
            
            for i, page in enumerate(pdf.pages):
                logger.info(f"Processando página {i+1}/{total_paginas}")
                try:
                    tables = page.extract_table()
                    if tables:
                        for row in tables:
                            if any(row):  
                                data.append(row)
                except Exception as e:
                    logger.warning(f"Erro ao extrair tabela da página {i+1}: {e}")
        
        if not data:
            logger.warning("Nenhuma tabela encontrada no PDF.")
            return None
            
        
        if len(data) <= 1:
            logger.warning("Dados insuficientes para criar um DataFrame com cabeçalho.")
            return None
            
        logger.info(f"Tabelas extraídas com sucesso. Total de linhas: {len(data)}")
        
        df = pd.DataFrame(data[1:], columns=data[0])
        
        
        df = df[~df.isin(df.columns).all(axis=1)]
        df = df.fillna(method='ffill')
        
        logger.info(f"DataFrame criado com sucesso. Dimensões: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao processar o PDF: {e}")
        return None

def substituir_abreviacoes(df):
    
    if df is None:
        logger.warning("DataFrame vazio, substituição de abreviações cancelada.")
        return None
        
    logger.info("Substituindo abreviações no DataFrame...")
    
    try:
        legenda = {
            "OD": "Procedimentos odontológicos",
            "AMB": "Procedimentos ambulatoriais"
        }
        
        # Cria uma cópia para evitar SettingWithCopyWarning
        df_processado = df.copy()
        df_processado.replace(legenda, inplace=True)
        
        logger.info("Abreviações substituídas com sucesso.")
        return df_processado
        
    except Exception as e:
        logger.error(f"Erro ao substituir abreviações: {e}")
        return df  # Retorna o DataFrame original em caso de erro

def salvar_e_compactar(df, nome_usuario, diretorio_saida=None):
    
    if df is None:
        logger.error("Nenhum dado para salvar. DataFrame vazio.")
        return False
    
    if diretorio_saida is None:
        diretorio_saida = obter_diretorio_saida()
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(diretorio_saida, f"Teste_{nome_usuario}.csv")
    zip_filename = os.path.join(diretorio_saida, f"Teste_{nome_usuario}.zip")
    zip_backup = os.path.join(diretorio_saida, f"Teste_{nome_usuario}_{timestamp}.zip")
    
    if os.path.exists(zip_filename):
        logger.info(f"Arquivo ZIP já existe. Criando backup: {zip_backup}")
        try:
            os.rename(zip_filename, zip_backup)
        except Exception as e:
            logger.warning(f"Não foi possível criar backup: {e}")
    
    try:
        logger.info(f"Salvando dados em {csv_filename}...")
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        logger.info(f"Compactando arquivo em {zip_filename}...")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(csv_filename, os.path.basename(csv_filename))
        
        # Remove o arquivo CSV temporário
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
            logger.info(f"Arquivo temporário {csv_filename} removido.")
        
        logger.info(f"Arquivo {zip_filename} gerado com sucesso!")
        print(f"\nArquivo salvo em: {zip_filename}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao salvar ou compactar o arquivo: {e}")
        return False

def processar_pdf(pdf_path=None, nome_usuario=NOME, diretorio_saida=None):
  
    if not pdf_path:
        pdf_path = encontrar_pdf()
        if not pdf_path:
            print("Erro: Não foi possível encontrar o arquivo PDF específico ou alternativas.")
            print("Por favor, especifique o caminho do arquivo manualmente.")
            return False
    
    logger.info(f"Iniciando processamento do PDF: {pdf_path}")
    
    if diretorio_saida is None:
        diretorio_saida = obter_diretorio_saida()
        
    zip_filename = os.path.join(diretorio_saida, f"Teste_{nome_usuario}.zip")
    if verificar_arquivo_existe(zip_filename):
        resposta = input(f"Arquivo {zip_filename} já existe. Deseja processá-lo novamente? (s/n): ").lower()
        if resposta != 's':
            logger.info("Processamento cancelado pelo usuário.")
            return False
    
    df = extrair_tabela_do_pdf(pdf_path)
    if df is not None:
        df = substituir_abreviacoes(df)
        resultado = salvar_e_compactar(df, nome_usuario, diretorio_saida)
        
        if resultado:
            logger.info("Processamento concluído com sucesso!")
            return True
    
    logger.error("Falha no processamento do PDF.")
    return False

if __name__ == "__main__":
    
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Erro: O arquivo especificado não existe: {pdf_path}")
            pdf_path = None
    

    print("\n=== EXTRATOR DE TABELAS PDF ===")
    print(f"Usuário atual: {NOME}")
    print(f"Arquivo alvo: {ARQUIVO}\n")
    
    if not pdf_path:
        print("Buscando arquivo automaticamente...")
        pdf_path = encontrar_pdf()
        if not pdf_path:
            print("Arquivo específico não encontrado automaticamente.")
            pdf_path = input("Digite o caminho completo do arquivo PDF (ou pressione Enter para cancelar): ")
            if not pdf_path:
                print("Operação cancelada.")
                sys.exit(1)
            if not os.path.exists(pdf_path):
                print(f"Erro: O arquivo não existe: {pdf_path}")
                sys.exit(1)
    
    if pdf_path and os.path.basename(pdf_path) != ARQUIVO:
        print(f"Nota: O arquivo encontrado ({os.path.basename(pdf_path)}) é diferente do arquivo alvo ({ARQUIVO}).")
        usar_arquivo = input("Deseja usar este arquivo? (s/n): ").lower()
        if usar_arquivo != 's':
            novo_caminho = input("Digite o caminho completo do arquivo correto (ou pressione Enter para cancelar): ")
            if not novo_caminho:
                print("Operação cancelada.")
                sys.exit(1)
            if not os.path.exists(novo_caminho):
                print(f"Erro: O arquivo não existe: {novo_caminho}")
                sys.exit(1)
            pdf_path = novo_caminho
    
    print(f"Processando o arquivo: {pdf_path}")
    resultado = processar_pdf(pdf_path, NOME)
    
    if resultado:
        print("\nProcessamento concluído com sucesso!")
    else:
        print("\nHouve um problema durante o processamento. Verifique o arquivo de log para detalhes.")