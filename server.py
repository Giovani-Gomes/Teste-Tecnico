from flask import Flask, request, jsonify
from flask_cors import CORS  
import pandas as pd

app = Flask(__name__)
CORS(app)  


try:
   
    operadoras_df = pd.read_csv('Relatorio_cadop.csv', encoding='utf-8', delimiter=';', quotechar='"')
except FileNotFoundError:
    print("Erro: O arquivo 'Relatorio_cadop.csv' não foi encontrado.")
    exit(1)
except pd.errors.ParserError:
    print("Erro: O arquivo 'Relatorio_cadop.csv' está corrompido ou não é um CSV válido.")
    exit(1)


operadoras_df = operadoras_df.dropna(how='all', axis=0)  
operadoras_df = operadoras_df.dropna(how='all', axis=1)  
operadoras_df = operadoras_df.fillna('')   

@app.route('/buscar_operadoras', methods=['GET'])
def buscar_operadoras():
    """
    Rota para busca por CNPJ
    """
    cnpj = request.args.get('cnpj', '').strip()

    if not cnpj:
        return jsonify({"erro": "CNPJ não fornecido"}), 400

  
    operadoras_df['CNPJ'] = operadoras_df['CNPJ'].astype(str)

 
    cnpj_limpo = cnpj.replace("-", "").replace(".", "").replace("/", "")
    
    
    resultado = operadoras_df[operadoras_df['CNPJ'].str.replace("-", "").replace(".", "").replace("/", "") == cnpj_limpo]

    if resultado.empty:
        return jsonify({"erro": "Operadora não encontrada com o CNPJ informado"}), 404

    return jsonify(resultado.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
