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

## Endpoint: `/api/v1/manage_students`

### Descrição
Este endpoint permite gerenciar estudantes em projetos, incluindo a adição e remoção de estudantes de um projeto.

### Métodos Possíveis
- `POST`: Adiciona estudantes a um projeto (somente para usuários com função de admin, coordenador ou orientador).
- `DELETE`: Remove estudantes de um projeto (somente para usuários com função de admin, coordenador ou orientador).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `students` (obrigatório): Lista de nomes de usuário dos estudantes.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido, nome do projeto nulo ou vazio, ou lista de estudantes ausente.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Projeto não encontrado.
- **500 Internal Server Error**: Erro ao gerenciar estudantes.

### Exemplo de Uso
```bash
# POST (Adiciona estudantes a um projeto)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "students": ["usuario1", "usuario2"]}' http://sua-api.com/api/v1/manage_students

# DELETE (Remove estudantes de um projeto)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "students": ["usuario1", "usuario2"]}' http://sua-api.com/api/v1/manage_students
```

Respostas de Exemplo

Sucesso (Adição ou Remoção de Estudantes)
```
{
  "msg": "Students managed successfully",
  "project_name": "Projeto Existente",
  "students": [
    {"studentId": "id_do_estudante_1", "studentName": "usuario1"},
    {"studentId": "id_do_estudante_2", "studentName": "usuario2"}
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
  "msg": "Unauthorized to manage students",
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

Erro (Estudante Não Encontrado ou Inválido)
```
{
  "msg": 'User "usuario1" not found or is not a valid student',
  "success": false
}
```

### Notas Adicionais

- A adição e remoção de estudantes exigem a função de admin, coordenador ou orientador.
- Os estudantes são identificados pelo nome de usuário, e a resposta inclui informações sobre os estudantes gerenciados.

## Endpoint: `/api/v1/manage_advisor`

### Descrição
Este endpoint permite gerenciar o orientador de um projeto, incluindo a atribuição e remoção de um orientador do projeto.

### Métodos Possíveis
- `POST`: Atribui um orientador a um projeto (somente para usuários com função de admin ou coordenador).
- `DELETE`: Remove o orientador de um projeto (somente para usuários com função de admin ou coordenador).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (POST e DELETE)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `advisor` (obrigatório): Nome de usuário do orientador.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido, nome do projeto nulo ou vazio, ou nome do orientador ausente.
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Projeto não encontrado.
- **500 Internal Server Error**: Erro ao gerenciar o orientador do projeto.

### Exemplo de Uso
```bash
# POST (Atribui orientador a um projeto)
curl -X POST -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "advisor": "orientador1"}' http://sua-api.com/api/v1/manage_advisor

# DELETE (Remove orientador de um projeto)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" -d '{"projectName": "Projeto Existente", "advisor": "orientador1"}' http://sua-api.com/api/v1/manage_advisor
```

Respostas de Exemplo

Sucesso (Atribuição ou Remoção de Orientador)
```
{
  "msg": "Advisor managed successfully",
  "project_name": "Projeto Existente",
  "advisor": {"advisorId": "id_do_orientador", "advisorName": "orientador1"},
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
  "msg": "Unauthorized to manage advisor",
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

Erro (Orientador Não Encontrado ou Inválido)
```
{
  "msg": 'User "orientador1" not found or is not a valid advisor',
  "success": false
}
```

### Notas Adicionais

- A atribuição e remoção do orientador exigem a função de admin ou coordenador.
- O orientador é identificado pelo nome de usuário, e a resposta inclui informações sobre o orientador gerenciado no projeto.