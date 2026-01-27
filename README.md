**Documentação da API**

Método,Endpoint,Função
GET,/livro/update/<id>,Consulta informações de um livro específico.
POST,/livro/post,Adiciona um novo livro (bloqueia se o ID já existir).
POST,/livro/upsert,Salva um livro (Cria novo ou atualiza se o ID já existir).
DELETE,/livro/delete/<id>,Remove permanentemente um livro do acervo.
