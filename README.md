# Documentação da API — Multimeios

Esta API expõe endpoints para gerenciar o acervo de livros. Nesta versão a representação dos registros usa o conjunto de colunas/atributos abaixo — os exemplos mostram JSON com as chaves exatamente como especificadas (com acentos e espaços quando aplicável). Observe que chaves com espaços ou caracteres especiais devem ser sempre enviadas entre aspas no JSON e com codificação UTF-8.

Base URL: `https://api-multimeios.onrender.com`  

---

## Colunas / Campos (modelo de dados)
Campos esperados para um registro de livro:

- "ID" (string) — identificador único (sempre enviado como string).
- "AUTOR" (string) — nome do(s) autor(es).
- "LIVRO" (string) — título do livro.
- "ESTANTE" (string) — localização física (ex.: sala/estante/prateleira).
- "VOLUME" (string, opcional) — número do volume, se houver.
- "EXEMPLAR" (string|int, opcional) — número do exemplar.
- "CIDADE" (string, opcional) — cidade de publicação.
- "EDITORA" (string, opcional) — editora.
- "ANO" (int|string, opcional) — ano de publicação.
- "ORIGEM" (string, opcional) — origem do acervo (doação, compra, permuta).
- "CÓDIGO" (string, opcional) — código interno ou tombo.
- "DATA" (string, opcional) — data relacionada (ex.: aquisição) no formato ISO 8601 (yyyy-mm-dd).
- "ADAPTADO POR" (string, opcional) — se aplicável, quem adaptou a obra.

Exemplo de objeto JSON (note as aspas nas chaves com espaço/acentos):
```json
{
  "ID": "123",
  "AUTOR": "Fulano de Tal",
  "LIVRO": "Exemplo de Livro",
  "ESTANTE": "A-3",
  "VOLUME": "1",
  "EXEMPLAR": "2",
  "CIDADE": "São Paulo",
  "EDITORA": "Editora Exemplo",
  "ANO": 2020,
  "ORIGEM": "Doação",
  "CÓDIGO": "TOMBO-0001",
  "DATA": "2024-05-10",
  "ADAPTADO POR": "Ciclano",
  "ALUGADO": "nao"
}
```

Exemplo de cabeçalho CSV (mesma ordem):
"ID","AUTOR","LIVRO","ESTANTE","VOLUME","EXEMPLAR","CIDADE","EDITORA","ANO","ORIGEM","CÓDIGO","DATA","ADAPTADO POR","ALUGADO"

---

## Endpoints

### 1) Consultar um registro
- Método: GET  
- Endpoint: `/livro/get/<ID>`  
- Descrição: Retorna o registro do livro com o `ID` informado.

Exemplo:
```bash
curl -X GET "https://api-multimeios.onrender.com/livro/get/123" \
  -H "Accept: application/json"
```

Resposta 200:
Retorna o objeto JSON conforme modelo acima.

Códigos possíveis:
- 200 OK — registro encontrado.
- 404 Not Found — não encontrado.
- 500 Internal Server Error — erro no servidor.

---

### 2) Criar um novo registro
- Método: POST  
- Endpoint: `/livro/post`  
- Descrição: Insere um novo livro; deve falhar se `ID` já existir (409 Conflict).

Exemplo:
```bash
curl -X POST "https://api-multimeios.onrender.com/livro/post" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "ID": "123",
    "AUTOR": "Fulano de Tal",
    "LIVRO": "Exemplo de Livro",
    "ESTANTE": "A-3",
    "VOLUME": "1",
    "EXEMPLAR": "2",
    "CIDADE": "São Paulo",
    "EDITORA": "Editora Exemplo",
    "ANO": 2020,
    "ORIGEM": "Doação",
    "CÓDIGO": "TOMBO-0001",
    "DATA": "2024-05-10",
    "ADAPTADO POR": "Ciclano"
  }'
```

Respostas:
- 201 Created — criado com sucesso.
- 400 Bad Request — payload inválido.
- 409 Conflict — ID já existe.
- 500 Internal Server Error.

---

### 3) Upsert (criar ou atualizar)
- Método: POST  
- Endpoint: `/livro/upsert`  
- Descrição: Se `ID` existir — atualiza; se não existir — cria.

Exemplo e códigos de resposta similares ao endpoint de criação:
- 200 OK — atualizado.
- 201 Created — criado.
- 400, 500 conforme aplicável.

---

### 4) Remover registro
- Método: DELETE  
- Endpoint: `/livro/delete/<ID>`  
- Descrição: Remove permanentemente o registro com o ID informado.

Exemplo:
```bash
curl -X DELETE "https://api-multimeios.onrender.com/livro/delete/123"
```

Respostas:
- 204 No Content — removido com sucesso.
- 404 Not Found — não encontrado.
- 500 Internal Server Error.

---

### 5) Alugar livro

- Método: POST
- Endpoint: /livro/alugar/<ID>
- Descrição: Localiza o livro pelo ID, altera o status para "sim", registra o nome do aluno e a data do aluguel. O sistema calcula automaticamente a DATA ENTREGA para 7 dias após a data informada.

Exemplo:

```Bash

curl -X POST "https://api-multimeios.onrender.com/livro/alugar/123" \
     -H "Content-Type: application/json" \
     -d '{"ALUNO": "Natan Matos", "DATA_ALUGUEL": "2026-02-01"}'
```
Respostas:
- 200 OK — Aluguel registrado e data de entrega calculada com sucesso.
- 404 Not Found — O ID do livro informado não existe no banco.
- 400 Bad Request — Formato de data inválido ou erro de comunicação com o banco/schema.
- 500 Internal Server Error — Falha inesperada no servidor.

---

### 6) Devolver livro
- Método: POST
- Endpoint: /livro/devolver/<ID>
- Descrição: Localiza o livro pelo ID, altera o valor da coluna ALUGADO para "não" e limpa os campos ALUNO, DATA ALUGUEL e DATA ENTREGA.

Exemplo:

```Bash

curl -X POST "https://api-multimeios.onrender.com/livro/devolver/123"
```
Respostas:
- 200 OK — Status alterado para "não" e registros de empréstimo limpos com sucesso.
- 404 Not Found — O ID do livro informado não existe no banco.
- 400 Bad Request — Erro de comunicação com o banco/schema.
- 500 Internal Server Error — Falha inesperada no servidor.

---

### 7) Listar livros alugados
- Método: GET
- Endpoint: `/livros/alugados`
- Descrição: Filtra o banco de dados e retorna apenas os livros que possuem o valor "sim" na coluna ALUGADO.

Exemplo:
```Bash
curl -X GET "https://api-multimeios.onrender.com/livros/alugados"
```

Respostas:
- 200 OK — Retorna a lista de livros alugados com sucesso.
- 400 Bad Request — Erro de comunicação com o banco/schema.
- 500 Internal Server Error — Falha inesperada no servidor.

---

### 8) Listar livros disponíveis
- Método: GET
- Endpoint: `/livros/disponiveis`
- Descrição: Filtra o banco de dados e retorna apenas os livros que possuem o valor "não" na coluna ALUGADO.

Exemplo:
```Bash
curl -X GET "https://api-multimeios.onrender.com/livros/disponiveis"
```
Respostas:
- 200 OK — Retorna a lista de livros disponíveis com sucesso.
- 400 Bad Request — Erro de comunicação com o banco/schema.
- 500 Internal Server Error — Falha inesperada no servidor.

---

## Observações técnicas e recomendações

- JSON aceita chaves com espaços e acentos; sempre usar aspas (ex.: `"ADAPTADO POR"`). Porém, por boas práticas de API é recomendado usar chaves sem espaços e sem acentos (ex.: `adaptado_por`, `ano`) para facilitar integração com clientes que possam ter limitações. Se optar por manter as chaves com espaços/acentos, documente claramente e mantenha consistência.
- Charset: use `Content-Type: application/json; charset=utf-8`.
- Padronize formatos (por exemplo, `DATA` em ISO 8601).
- Retorne estrutura de erro consistente:
```json
{
  "error": {
    "code": "BAD_REQUEST",
    "message": "Campo obrigatorio ausente",
    "details": { "LIVRO": "campo obrigatório" }
  }
}
```

---

