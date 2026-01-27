import os
from flask import Flask, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. Carregamos as variáveis
load_dotenv()
app = Flask(__name__)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# 2. Criamos o cliente da forma MAIS SIMPLES possível
# Sem usar o parâmetro 'options', evitamos o erro de 'storage' ou 'headers'
supabase: Client = create_client(url, key)

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
    


# Rota para a buscar o livro por id
@app.route('/livro/get/<livro_id>')
def buscar_por_id(livro_id):
    try:
        # faz a busca na supabase
        response = (
            supabase.schema("biblioteca") # vai no schema
            .table('livro') # encontra a table
            .select("*") # faz o select *
            .delete()
            .eq("ID", str(livro_id)) # pega o ID
            .execute()
        )
        
        if not response.data:
            return jsonify({"erro": f"Livro com ID '{livro_id}' não encontrado"}), 404

        return jsonify({"mensagem": "Livro eliminado com sucesso!",
            "item_removido": response.data[0]})

    except Exception as e:
        return jsonify({"erro_interno": str(e)}), 500

@app.route('/livro/delete/<livro_id>')
def apagar_por_id(livro_id):
    try:
        response = (
            supabase.schema("biblioteca")
            .table("livro")
            .select("*")
            .eq("ID", str(livro_id))
            .execute()
        )

        if not response.data:
            return jsonify({"erro": f"Livro com id'{livro_id}' não encontrado"}), 404
        
        return jsonify({"Resposta": f"Livro '{response.data[0]["LIVRO"]}' apagado com sucesso"})
    
    except Exception as e:
        return jsonify({"erro interno":str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)