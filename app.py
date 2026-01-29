import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Carregamos as variáveis
load_dotenv()
app = Flask(__name__)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")


supabase: Client = create_client(url, key)


#Rota a ser alterada
@app.route('/')
def index():
    try:
        response = supabase.schema("biblioteca").table('livro').select("*").execute()
        
        # Se chegar aqui, a conexão funcionou!
        if not response.data:
            return "<h1>Conectado!</h1><p>Mas a tabela 'livro' no esquema 'biblioteca' retornou 0 registros.</p>"
        
        return jsonify(response.data)

    except Exception as e:
        # Se houver erro de permissão (RLS), ele aparecerá aqui
        return f"<h1>Erro de Banco:</h1><p>{str(e)}</p>"
    


# Rota pra a buscar o livro por id
@app.route('/livro/get/<livro_id>')
def buscar_por_id(livro_id):
    try:
        # faz a busca na supabase
        response = (
            supabase.schema("biblioteca") # vai no schema
            .table('livro') # encontra a table
            .select("*") # faz o select *
            .eq("ID", str(livro_id)) # pega o ID
            .execute()
        )
        
        if not response.data:
            return jsonify({"erro": f"Livro com ID '{livro_id}' não encontrado"}), 404

        return jsonify(response.data[0])

    except Exception as e:

        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500



# Rota pra deletar o livro por id
@app.route('/livro/delete/<livro_id>')
def apagar_por_id(livro_id):
    try:
        response = (
            supabase.schema("biblioteca")
            .table("livro")
            .delete()
            .eq("ID", str(livro_id))
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Livro com id'{livro_id}' não encontrado"}), 404
        
        return jsonify({"Resposta": f"Livro '{response.data[0]["LIVRO"]}' apagado com sucesso"})
    
    except Exception as e:

        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


@app.route('/livro/post', methods=['POST'])
def adicionar_livro_completo():
    try:
        dados = request.get_json()

        # Montamos o dicionário com os nomes das colunas do banco
        novo_registro = {
            "ID": str(dados.get('ID')),
            "AUTOR": dados.get('AUTOR'),
            "LIVRO": dados.get('LIVRO'),
            "ESTANTE": dados.get('ESTANTE'),
            "VOLUME": dados.get('VOLUME'),
            "EXEMPLAR": dados.get('EXEMPLAR'),
            "CIDADE": dados.get('CIDADE'),
            "EDITORA": dados.get('EDITORA'),
            "ANO": dados.get('ANO'),
            "ORIGEM": dados.get('ORIGEM'),
            "CÓDIGO": dados.get('CÓDIGO'), 
            "DATA": dados.get('DATA'),
            "ADAPTADO POR": dados.get('ADAPTADO_POR') 
        }

        # Validação mínima (ID e LIVRO são essenciais)
        if not novo_registro["ID"] or not novo_registro["LIVRO"]:
            return jsonify({"erro": "ID e LIVRO são campos obrigatórios"}), 400

        # Inserção no Supabase
        response = (
            supabase.schema("biblioteca")
            .table('livro')
            .insert(novo_registro)
            .execute()
        )

        return jsonify({
            "status": "sucesso",
            "dados_inseridos": response.data[0]
        }), 201

    except Exception as e:

        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


    
@app.route('/livro/upsert', methods=['POST'])
def upsert_livro():
    try:
        dados = request.get_json()
        
        # O dicionário com todas as colunas que definidas antes
        registro = {
            "ID": str(dados.get('ID')),
            "AUTOR": dados.get('AUTOR'),
            "LIVRO": dados.get('LIVRO'),
            "ESTANTE": dados.get('ESTANTE'),
            "VOLUME": dados.get('VOLUME'),
            "EXEMPLAR": dados.get('EXEMPLAR'),
            "CIDADE": dados.get('CIDADE'),
            "EDITORA": dados.get('EDITORA'),
            "ANO": dados.get('ANO'),
            "ORIGEM": dados.get('ORIGEM'),
            "CÓDIGO": dados.get('CÓDIGO'), 
            "DATA": dados.get('DATA'),
            "*ADAPTADO POR": dados.get('ADAPTADO_POR') 
        }

        # O comando .upsert() usa a "Primary Key" (o ID) para decidir 
        # se cria ou se atualiza.
        response = (
            supabase.schema("biblioteca")
            .table('livro')
            .upsert(registro) 
            .execute()
        )

        return jsonify({
            "status": "sucesso (upsert)",
            "dados": response.data[0]
        }), 201

    except Exception as e:

        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Rota para alugar um livro
@app.route('/livro/alugar/<id_item>', methods=['POST'])
def alugar_livro(id_item):
    try:
        # Realiza o update na tabela 'livro' onde o ID coincide com o fornecido
        # Define a coluna 'ALUGADO' como 'sim'
        data = supabase.schema("biblioteca").table("livro").update({"ALUGADO": "sim"}).eq("ID", id_item).execute()
        
        # Verifica se o livro foi encontrado e atualizado
        if len(data.data) > 0:
            return jsonify({"mensagem": f"Livro {id_item} alugado com sucesso!", "dados": data.data}), 200
        else:
            return jsonify({"erro": "Livro não encontrado"}), 404
            
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)