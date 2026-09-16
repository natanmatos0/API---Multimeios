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
        response = supabase.schema("biblioteca").table('livros').select("*").execute()
        
        # Se chegar aqui, a conexão funcionou!
        if not response.data:
            return "<h1>Conectado!</h1><p>Mas a tabela 'livro' no esquema 'biblioteca' retornou 0 registros.</p>"
        
        return jsonify(response.data)

    except Exception as e:
        # Se houver erro de permissão (RLS), ele aparecerá aqui
        return f"<h1>Erro de Banco:</h1><p>{str(e)}</p>"

@app.route('/total')
def indext():
    try:
        response = supabase.schema("biblioteca").table('livros').select('*').execute()
        if not response.data:
            return "<h1>Conectado!</h1><p>Mas a tabela 'livros' no esquema 'biblioteca' retornou 0 registros</p>"
        
        return jsonify(response.data)
    
    except Exception as e:
        return f"<h1>Erro de Banco:</h1><p>{str(e)}</p>"



@app.route('/livros/<livro_titulo>')
def buscars_por_titulo(livro_titulo):
    try:
        response = (
            supabase.schema("biblioteca") 
            .table("livros")              
            .select("*")                  
            .ilike("titulo", f"{livro_titulo}%")  
            .execute()
)

        if not response.data:
            return jsonify({"erro": f"Livro '{livro_titulo}' nao encontrado"})

        return jsonify(response.data)
        
    except Exception as e:
        print(f"Erro {str(e)}")
        return jsonify({"Erro_detalhado": str(e)}), 500


@app.route('/livros/post', methods=['POST'])
def castro_de_livros():
    try:
        dados = request.get_json()

        novo_registro = {
            "numero_de_registro": dados.get("numero_de_registro"),
            "titulo": dados.get("titulo"),
            "autor": dados.get("autor"),
            "genero": dados.get("genero"),
            "categoria": dados.get("categoria"),
            "localizacao": dados.get("localizacao"),
            "observacoes": dados.get("observacoes")
        }
        if not novo_registro["numero_de_registro"] or not novo_registro["titulo"]:
            return jsonify({"erro": "Registro e Titulo são campos obrigatorios"})
    
        response = (
            supabase.schema("biblioteca")
            .table("livros")
            .insert(novo_registro)
            .execute()
            )
    
        return jsonify({
            "status": "sucesso",
            "dados_inseridos": response.data[0]
        }), 201

    except Exception as e:
        print(f"Erro {str(e)}")
        return jsonify({"erro_datalhaado": str(e)}), 500
    
    
@app.route('/livro/<livro_titulo>')
def buscar_por_titulo(livro_titulo):
    try:
        response = (
            supabase.schema("biblioteca")
            .table('livro')
            .select('*')
            .eq("LIVRO",livro_titulo)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Livro '{livro_titulo}' nao encontrado"})

        return jsonify(response.data)
        
    except Exception as e:
        print(f"Erro {str(e)}")
        return jsonify({"Erro_detalhado": str(e)}), 500

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
    
@app.route('/livros/alugar/<id_item>', methods=['POST'])
def alugar_livros(id_item):
    try:
        dados_recebidos = request.get_json()
        
        nome_aluno = dados_recebidos.get('aluno')
        data_aluguel_str = dados_recebidos.get('data_aluguel') 

        data_aluguel_obj = datetime.strptime(data_aluguel_str, "%Y-%m-%d")
        data_entrega_obj = data_aluguel_obj + timedelta(days=14)
        data_entrega_str = data_entrega_obj.strftime("%Y-%m-%d")


        res = (
            supabase.schema("biblioteca")
            .table("livros")
            .update({
                "alugado": "sim",      
                "aluno": nome_aluno,     
                "data_aluguel": data_aluguel_str,
                "data_entrega": data_entrega_str 
            })
            .eq("numero_de_registro", id_item) 
            .execute()
        )
        
        if res.data:
            return jsonify({
                "status": "sucesso", 
                "mensagem": f"Livro alugado para {nome_aluno}. Entrega em {data_entrega_str}.",
                "dados": res.data[0]
            }), 200
        
        return jsonify({"erro": "Livro não encontrado com este número de registro"}), 404

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

@app.route('/livros/renovar/<id_item>', methods=['POST'])
def renovar_livro(id_item):
    try:
        #busca o livro
        res_livro = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("alugado", "data_entrega")
            .eq("numero_de_registro", id_item)
            .execute()
        )

        #Validação do livro
        if not res_livro.data:
            return jsonify({"erro": "Livro não encontrado com este número de registro"}), 404

        livro = res_livro.data[0]

        #Validação do aluguel
        if livro.get("alugado") != "sim" or not livro.get("data_entrega"):
            return jsonify({"erro": "Este livro não está alugado atualmente para ser renovado"}), 400

        #adiciona mais 14 dias a data
        data_entrega_atual_str = livro["data_entrega"]
        data_entrega_obj = datetime.strptime(data_entrega_atual_str, "%Y-%m-%d")
        
        nova_data_entrega_obj = data_entrega_obj + timedelta(days=14)
        nova_data_entrega_str = nova_data_entrega_obj.strftime("%Y-%m-%d")

        #atualiza a data no banco
        res_update = (
            supabase.schema("biblioteca")
            .table("livros")
            .update({
                "data_entrega": nova_data_entrega_str
            })
            .eq("numero_de_registro", id_item)
            .execute()
        )

        if res_update.data:
            return jsonify({
                "status": "sucesso",
                "mensagem": f"Livro renovado com sucesso! Nova data de entrega: {nova_data_entrega_str}.",
                "dados": res_update.data[0]
            }), 200

        return jsonify({"erro": "Erro ao atualizar a data de renovação"}), 500

    except Exception as e:
        return jsonify({"erro_detalhado": str(e)}), 400

@app.route('/livros/devolver/<id_item>', methods=['POST'])
def devolver_livros(id_item):
    try:
        res = (
            supabase.schema("biblioteca")
            .table("livros")
            .update({
                "alugado": "não",
                "aluno": None,
                "data_aluguel": None,
                "data_entrega": None
            })
            .eq("numero_de_registro", id_item)
            .execute()
        )
        
        if res.data:
            return jsonify({"status": "sucesso", "mensagem": "Livro devolvido com sucesso!"}), 200
        
        return jsonify({"erro": "Livro não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 400

# Rota para LISTAR apenas livros alugados
@app.route('/livros/alugados', methods=['GET'])
def listar_alugados():
    try:
        res = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("*")
            .ilike("alugado", "sim%")
            .execute()
        )
        return jsonify(res.data), 200
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




# Cadastrar um novo aluno
@app.route('/alunos', methods=['POST'])
def cadastrar_aluno():
    try:
        dados = request.get_json()

        novo_aluno = {
            "nome": dados.get("nome"),
            "curso": dados.get("curso"),
            "ano": dados.get("ano")
        }

        # Validação dos campos obrigatórios
        if not novo_aluno["nome"] or not novo_aluno["curso"] or novo_aluno["ano"] is None:
            return jsonify({"erro": "Os campos 'nome', 'curso' e 'ano' são obrigatórios"}), 400

        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .insert(novo_aluno)
            .execute()
        )

        return jsonify({
            "status": "sucesso",
            "aluno_cadastrado": response.data[0]
        }), 201

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Listar todos os alunos
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    try:
        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("*")
            .execute()
        )

        return jsonify(response.data), 200

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Buscar aluno por ID
@app.route('/alunos/<aluno_id>', methods=['GET'])
def buscar_aluno(aluno_id):
    try:
        response = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("*")
            .eq("id", aluno_id)
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        return jsonify(response.data[0]), 200

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Alugar um livro para um aluno
@app.route('/alunos/<aluno_id>/alugar/<numero_registro>', methods=['POST'])
def aluno_alugar_livro(aluno_id, numero_registro):
    try:
        # 1. Verifica se o aluno existe
        res_aluno = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("id, nome")
            .eq("id", aluno_id)
            .execute()
        )
        if not res_aluno.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        # 2. Verifica se o livro existe e está disponível
        res_livro = (
            supabase.schema("biblioteca")
            .table("livros")
            .select("numero_de_registro, titulo, alugado")
            .eq("numero_de_registro", numero_registro)
            .execute()
        )
        if not res_livro.data:
            return jsonify({"erro": f"Livro '{numero_registro}' não encontrado"}), 404

        livro = res_livro.data[0]
        if livro.get("alugado") == "sim":
            return jsonify({"erro": "Este livro já está alugado no momento"}), 409

        # 3. Calcula as datas — data de aluguel é sempre hoje, devolução sempre +14 dias
        data_aluguel_str = datetime.now().strftime("%Y-%m-%d")
        data_entrega_prevista_str = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

        # 4. Registra o empréstimo na tabela emprestimos
        novo_emprestimo = {
            "aluno_id": aluno_id,
            "numero_de_registro": numero_registro,
            "data_aluguel": data_aluguel_str,
            "data_entrega_prevista": data_entrega_prevista_str,
            "status": "ativo"
        }
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .insert(novo_emprestimo)
            .execute()
        )

        # 5. Atualiza o status do livro para alugado
        supabase.schema("biblioteca").table("livros").update({
            "alugado": "sim",
            "aluno": res_aluno.data[0]["nome"]
        }).eq("numero_de_registro", numero_registro).execute()

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Livro '{livro['titulo']}' alugado para {res_aluno.data[0]['nome']}. Devolução até {data_entrega_prevista_str}.",
            "emprestimo": res_emprestimo.data[0]
        }), 201

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Devolver um livro de um aluno
@app.route('/alunos/<aluno_id>/devolver/<numero_registro>', methods=['POST'])
def aluno_devolver_livro(aluno_id, numero_registro):
    try:
        # 1. Busca o empréstimo ativo desse aluno com esse livro
        res_emprestimo = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("*")
            .eq("aluno_id", aluno_id)
            .eq("numero_de_registro", numero_registro)
            .eq("status", "ativo")
            .execute()
        )

        if not res_emprestimo.data:
            return jsonify({"erro": "Nenhum empréstimo ativo encontrado para este aluno e livro"}), 404

        emprestimo = res_emprestimo.data[0]
        data_devolucao_real = datetime.now().strftime("%Y-%m-%d")

        # 2. Atualiza o empréstimo como devolvido
        supabase.schema("biblioteca").table("emprestimos").update({
            "status": "devolvido",
            "data_devolucao_real": data_devolucao_real
        }).eq("id", emprestimo["id"]).execute()

        # 3. Libera o livro na tabela livros
        supabase.schema("biblioteca").table("livros").update({
            "alugado": "não",
            "aluno": None,
            "data_aluguel": None,
            "data_entrega": None
        }).eq("numero_de_registro", numero_registro).execute()

        return jsonify({
            "status": "sucesso",
            "mensagem": f"Livro '{numero_registro}' devolvido com sucesso em {data_devolucao_real}."
        }), 200

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


# Histórico de empréstimos de um aluno
@app.route('/alunos/<aluno_id>/historico', methods=['GET'])
def historico_aluno(aluno_id):
    try:
        # Verifica se o aluno existe
        res_aluno = (
            supabase.schema("biblioteca")
            .table("alunos")
            .select("id, nome")
            .eq("id", aluno_id)
            .execute()
        )
        if not res_aluno.data:
            return jsonify({"erro": f"Aluno com ID '{aluno_id}' não encontrado"}), 404

        # Busca todos os empréstimos do aluno
        res_historico = (
            supabase.schema("biblioteca")
            .table("emprestimos")
            .select("*")
            .eq("aluno_id", aluno_id)
            .order("data_aluguel", desc=True)
            .execute()
        )

        return jsonify({
            "aluno": res_aluno.data[0]["nome"],
            "total_emprestimos": len(res_historico.data),
            "historico": res_historico.data
        }), 200

    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"erro_detalhado": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)