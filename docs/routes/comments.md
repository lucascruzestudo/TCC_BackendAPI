## Endpoint: `/api/v1/comments`

### Descrição
Este endpoint permite gerenciar comentários associados a arquivos de projetos, incluindo adição e exclusão de comentários.

### Métodos Possíveis
- `POST`: Adiciona um comentário a um arquivo específico de um estágio de um projeto (somente para orientadores e alunos).
- `DELETE`: Remove um comentário de um arquivo específico de um estágio de um projeto (somente para orientadores e alunos).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `stageId` (obrigatório): ID do estágio do projeto.
  - `filename` (obrigatório): Nome do arquivo.
  - `comment` (opcional, somente para POST): Texto do comentário.

- **Corpo da Resposta**:
  - `msg`: Mensagem indicando o resultado da operação.
  - `success`: Indica se a operação foi bem-sucedida.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido, nome do projeto nulo ou vazio, ID do estágio inválido, ou tipo de arquivo não permitido.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Projeto não encontrado ou arquivo não encontrado.
- **500 Internal Server Error**: Erro ao gerenciar comentários.

### Exemplo de Uso
```bash
# POST (Adiciona comentário a um arquivo)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "stageId": 1, "filename": "arquivo1.txt", "comment": "Comentário sobre o arquivo"}' http://sua-api.com/api/v1/comments

# DELETE (Remove comentário de um arquivo)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "stageId": 1, "filename": "arquivo1.txt", "commentId": "id_do_comentario"}' http://sua-api.com/api/v1/comments
```

Respostas de Exemplo

Sucesso (Adição de Comentário)
```
{
  "msg": "Comment added successfully",
  "success": true
}
```

Sucesso (Remoção de Comentário)
```
{
  "msg": "Comment deleted successfully",
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
  "msg": "Unauthorized to manage comments",
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

Erro (Arquivo Não Encontrado)
```
{
  "msg": "File not found in the specified stage",
  "success": false
}
```

Erro (Erro Interno do Servidor)
```
{
  "msg": "Internal Server Error",
  "success": false
}
```

### Notas Adicionais

- A adição e remoção de comentários são permitidas apenas para orientadores e alunos.
- É possível adicionar vários comentários ao mesmo arquivo.
- Comentários são associados a arquivos específicos em estágios específicos de projetos.