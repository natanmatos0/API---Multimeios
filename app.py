import os
from flask import Flask, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS
import json

# 1. Carregamos as variáveis
load_dotenv()
app = Flask(__name__)
CORS(app)

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
from datetime import datetime, timedelta

@app.route('/livro/alugar/<id_item>', methods=['POST'])
def alugar_livro(id_item):
    try:
        dados_recebidos = request.get_json()
        
        nome_aluno = dados_recebidos.get('ALUNO')
        data_aluguel_str = dados_recebidos.get('DATA_ALUGUEL') # Recebe "YYYY-MM-DD"

        # Converte a string da data para um objeto datetime para poder somar dias
        data_aluguel_obj = datetime.strptime(data_aluguel_str, "%Y-%m-%d")
        
        # Calcula a data de entrega (7 dias depois)
        data_entrega_obj = data_aluguel_obj + timedelta(days=7)
        
        # Converte de volta para string para salvar no banco
        data_entrega_str = data_entrega_obj.strftime("%Y-%m-%d")

        # Atualiza as colunas no Supabase
        res = supabase.schema("biblioteca").table("livro").update({
            "ALUGADO": "sim",
            "ALUNO": nome_aluno,
            "DATA ALUGUEL": data_aluguel_str,
            "DATA ENTREGA": data_entrega_str  # Nome exato da sua coluna no banco
        }).eq("ID", id_item).execute()
        
        if res.data:
            return jsonify({
                "status": "sucesso", 
                "mensagem": f"Livro alugado para {nome_aluno}. Entrega em {data_entrega_str}."
            }), 200
        
        return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    

# Rota para DEVOLVER um livro
@app.route('/livro/devolver/<id_item>', methods=['POST'])
def devolver_livro(id_item):
    try:
        # Atualiza ALUGADO para 'não' e limpa os campos de registro de empréstimo
        res = supabase.schema("biblioteca").table("livro").update({
            "ALUGADO": "não",
            "ALUNO": None,
            "DATA ALUGUEL": None,
            "DATA ENTREGA": None
        }).eq("ID", id_item).execute()
        
        if res.data:
            return jsonify({
                "status": "sucesso", 
                "mensagem": f"Livro {id_item} devolvido e registros limpos."
            }), 200
            
        return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Rota para LISTAR apenas livros alugados
@app.route('/livros/alugados', methods=['GET'])
def listar_alugados():
    try:
        # Filtra na tabela 'livro' onde 'ALUGADO' é igual a 'sim'
        res = supabase.schema("biblioteca").table("livro").select("*").eq("ALUGADO", "sim").execute()
        
        return jsonify({
            "quantidade": len(res.data),
            "livros_alugados": res.data
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400


# Rota para LISTAR livros disponíveis (não alugados)
@app.route('/livros/disponiveis', methods=['GET'])
def listar_disponiveis():
    try:
        # Filtra onde 'ALUGADO' é 'não'
        res = supabase.schema("biblioteca").table("livro").select("*").eq("ALUGADO", "não").execute()
        
        return jsonify({
            "quantidade": len(res.data),
            "livros_disponiveis": res.data
        }), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    

# Carrega a string do .env e converte para uma lista de dicionários
usuarios_permitidos = json.loads(os.getenv("LISTA_USUARIOS", "[]"))

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        user_input = data.get("user")
        pass_input = data.get("pass")

        # Procura na lista carregada do .env se existe o par user/pass
        usuario_valido = any(u['user'] == user_input and u['pass'] == pass_input for u in usuarios_permitidos)

        if usuario_valido:
            return jsonify({
                "success": True, 
                "mensagem": f"Bem-vindo, {user_input}!"
            }), 200

        return jsonify({"success": False, "mensagem": "Usuário ou senha incorretos"}), 401

    except Exception as e:
        return jsonify({"success": False, "erro": "Erro ao processar login"}), 500
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)