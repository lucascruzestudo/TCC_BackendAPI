## Endpoint: `/api/v1/files`

### Descrição
Este endpoint permite visualizar, gerenciar e comentar em arquivos associados a estágios de projetos.

### Métodos Possíveis
- `GET`: Recupera informações sobre os arquivos associados a um estágio de um projeto.
- `POST`: Faz upload de um arquivo para um estágio de um projeto (somente para orientadores e alunos).
- `DELETE`: Exclui um arquivo de um estágio de um projeto (somente para orientadores e alunos).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Parâmetros da Requisição (GET)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `stageId` (obrigatório): ID do estágio.

- **Parâmetros do Formulário da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `stageId` (obrigatório): ID do estágio.
  - `title` (opcional): Título do arquivo.
  - `file` (opcional, POST): Arquivo a ser enviado.
  - `fileName` (opcional, DELETE): Nome do arquivo a ser excluído.

### Possíveis Erros
- **400 Bad Request**: Parâmetros inválidos, nenhum arquivo selecionado (POST), tipo de arquivo inválido (POST), ou nome do projeto/nome do estágio nulo ou vazio.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Projeto não encontrado, arquivo não encontrado no estágio especificado.
- **500 Internal Server Error**: Erro ao gerenciar arquivos.

### Exemplo de Uso
```bash
# GET (Recupera informações sobre arquivos em um estágio)
curl -X GET -H "Authorization: Bearer seu_token_de_acesso" -d "projectName=Projeto Existente&stageId=1" http://sua-api.com/api/v1/files

# POST (Faz upload de um arquivo para um estágio)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -F "projectName=Projeto Existente" -F "stageId=1" -F "file=@caminho/do/seu/arquivo.txt" -F "title=Título do Arquivo" http://sua-api.com/api/v1/files

# DELETE (Exclui um arquivo de um estágio)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -F "projectName=Projeto Existente" -F "stageId=1" -F "fileName=arquivo.txt" http://sua-api.com/api/v1/files
```

Respostas de Exemplo

Sucesso (Recuperação de Arquivos)
```
{
  "files": [
    {
      "title": "Título do Arquivo",
      "filename": "arquivo.txt",
      "status": 0,
      "comments": [
        {
          "_id": "id_do_comentario",
          "user_id": "id_do_usuario",
          "username": "nome_do_usuario",
          "comment_text": "Texto do Comentário",
          "timestamp": "timestamp_do_comentario"
        }
      ]
    }
  ],
  "success": true
}
```

Sucesso (Upload de Arquivo)
```
{
  "msg": "File uploaded successfully",
  "success": true
}
```

Sucesso (Exclusão de Arquivo)
```
{
  "msg": "File deleted successfully",
  "success": true
}
```

Erro (Parâmetros Inválidos)
```
{
  "msg": "Invalid stage ID format",
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

Erro (Arquivo Não Encontrado no Estágio Especificado)
```
{
  "msg": "File not found in the specified stage",
  "success": false
}
```

### Notas Adicionais

- A recuperação de arquivos está disponível para orientadores e alunos associados ao projeto.
- A adição e remoção de arquivos estão disponíveis apenas para orientadores e alunos associados ao projeto.
- Os arquivos podem ter um título associado e incluem comentários feitos pelos usuários.