## Endpoint: `/api/v1/manage_projects`

### Descrição
Este endpoint permite gerenciar projetos, incluindo a recuperação, criação e exclusão de projetos.

### Métodos Possíveis
- `GET`: Recupera os projetos com base no papel do usuário.
- `POST`: Cria um novo projeto (somente para usuários com função de admin ou coordenador).
- `DELETE`: Exclui um projeto pelo nome (somente para usuários com função de admin ou coordenador).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório para POST e DELETE): Nome do projeto.

### Possíveis Erros
- **400 Bad Request**: Nome do projeto não pode ser nulo ou vazio.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Usuário não encontrado (no caso de GET) ou projeto não encontrado para exclusão.
- **500 Internal Server Error**: Erro ao recuperar ou criar projetos.

### Exemplo de Uso
```bash
# GET (Recupera projetos)
curl -X GET -H "Authorization: Bearer seu_token_de_acesso" http://sua-api.com/api/v1/manage_projects

# POST (Cria projeto)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Novo Projeto"}' http://sua-api.com/api/v1/manage_projects

# DELETE (Exclui projeto)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente"}' http://sua-api.com/api/v1/manage_projects
```

Respostas de Exemplo

Sucesso (Recuperação de Projetos)
```
{
  "msg": "Projects retrieved successfully",
  "success": true,
  "projects": [...]
}
```

Sucesso (Criação de Projeto)
```
{
  "msg": "Project created successfully",
  "success": true
}
```

Sucesso (Exclusão de Projeto)
```
{
  "msg": "Project deleted successfully",
  "success": true
}
```

Erro (Nome do Projeto Nulo ou Vazio)
```
{
  "msg": "Project name cannot be null or empty",
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
  "msg": "Unauthorized to create project",
  "success": false
}
```

Erro (Projeto Não Encontrado)
```
{
  "msg": "Project not found or you do not have permission to delete it",
  "success": false
}
```

### Notas Adicionais

- A recuperação de projetos é condicional ao papel do usuário (admin, coordenador, orientador, aluno).
- A criação e exclusão de projetos exigem função de admin ou coordenador.