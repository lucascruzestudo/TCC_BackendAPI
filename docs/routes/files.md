## Endpoint: `/api/v1/files`

### Descrição
Este endpoint permite gerenciar arquivos associados a projetos, incluindo upload, exclusão e recuperação de arquivos.

### Métodos Possíveis
- `POST`: Adiciona um arquivo a um estágio específico de um projeto (somente para orientadores e alunos).
- `DELETE`: Remove um arquivo de um estágio específico de um projeto (somente para orientadores e alunos).
- `GET`: Recupera informações sobre os arquivos de um estágio específico de um projeto (somente para coordenadores e orientadores).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `stageId` (obrigatório): ID do estágio do projeto.
  - `title` (obrigatório): Título do arquivo.

- **Parâmetros da Requisição (GET)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `stageId` (obrigatório): ID do estágio do projeto.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido, nome do projeto nulo ou vazio, ID do estágio inválido, ou tipo de arquivo não permitido.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Projeto não encontrado.

### Exemplo de Uso
```bash
# POST (Adiciona arquivo a um estágio)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -F "projectName=Projeto Existente" -F "stageId=1" -F "title=Arquivo 1" -F "file=@caminho/do/seu/arquivo.txt" http://sua-api.com/api/v1/files

# DELETE (Remove arquivo de um estágio)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -F "projectName=Projeto Existente" -F "stageId=1" -F "title=Arquivo 1" http://sua-api.com/api/v1/files

# GET (Recupera informações sobre arquivos de um estágio)
curl -X GET -H "Authorization: Bearer seu_token_de_acesso" -G --data-urlencode "projectName=Projeto Existente" --data-urlencode "stageId=1" http://sua-api.com/api/v1/files
```

Respostas de Exemplo

Sucesso (Upload de Arquivo)
```
{
  "msg": "File uploaded successfully",
  "success": true
}
```

Sucesso (Remoção de Arquivo)
```
{
  "msg": "File deleted successfully",
  "success": true
}
```

Sucesso (Recuperação de Informações sobre Arquivos)
```
{
  "files": [
    {
      "title": "Arquivo 1",
      "filename": "arquivo1.txt",
      "status": 0,
      "comments": []
    },
    {
      "title": "Arquivo 2",
      "filename": "arquivo2.txt",
      "status": 1,
      "comments": [
        {
          "_id": "id_do_comentario",
          "user_id": "id_do_usuario",
          "username": "usuario1",
          "comment_text": "Comentário sobre o arquivo",
          "timestamp": "2023-01-01T12:34:56"
        }
      ]
    }
  ],
  "success": true
}
```

Erro (Corpo da Requisição Inválido)
```
{
  "msg": "Invalid request body",
  "success": false
}
```

Erro (Token de Acesso Inválido)
```
{
  "msg": "Invalid access token",
  "success": false
}
```

Erro (Usuário Não Autorizado)
```
{
  "msg": "Unauthorized to manage files",
  "success": false
}
```

Erro (Projeto Não Encontrado)
```
{
  "msg": "Project not found",
  "success": false
}
```

Erro (Tipo de Arquivo Não Permitido)
```
{
  "msg": "Invalid file type",
  "success": false
}
```

### Notas Adicionais

- A adição e remoção de arquivos são permitidas apenas para orientadores e alunos.
- A recuperação de informações sobre arquivos é permitida apenas para coordenadores e orientadores.