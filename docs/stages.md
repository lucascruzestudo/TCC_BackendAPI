## Endpoint: `/api/v1/stages/approve`

### Descrição
Este endpoint é utilizado para aprovar a etapa atual de um projeto. Apenas orientadores podem realizar essa ação.

### Métodos Possíveis
- `POST`: Aprova a etapa atual do projeto.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `projectName` (obrigatório): Nome do projeto a ser aprovado.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido.
- **403 Forbidden**: Usuário não autorizado a aprovar etapas.
- **404 Not Found**: Projeto não encontrado ou usuário não é orientador do projeto.
- **500 Internal Server Error**: Erro interno ao aprovar a etapa.

### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/approve -d '{"projectName": "nome_do_projeto"}'
```

Respostas de Exemplo

Sucesso (Aprovação de Etapa)
```
{
  "msg": "Stage approved successfully",
  "success": true
}
```

Erro (Projeto já Concluído)
```
{
  "msg": "Cannot approve further stages, project is already completed",
  "success": false
}
```

## Endpoint: `/api/v1/stages/revert`

### Descrição
Este endpoint é utilizado para reverter a etapa atual de um projeto. Apenas orientadores podem realizar essa ação.

### Métodos Possíveis
- `POST`: Reverte a etapa atual do projeto.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `projectName` (obrigatório): Nome do projeto a ser revertido.

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido.
- **403 Forbidden**: Usuário não autorizado a reverter etapas.
- **404 Not Found**: Projeto não encontrado ou usuário não é orientador do projeto.
- **500 Internal Server Error**: Erro interno ao reverter a etapa.

### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/revert -d '{"projectName": "nome_do_projeto"}'
```

Respostas de Exemplo

Sucesso (Reversão de Etapa)
```
{
  "msg": "Stage reverted successfully",
  "success": true
}
```

Erro (Etapa 1 não pode ser revertida)
```
{
  "msg": "Cannot revert stage 1",
  "success": false
}
```

## Endpoint: `/api/v1/stages/setDueDate`

### Descrição
Este endpoint é utilizado para definir a data de vencimento para a etapa atual de um projeto. Apenas orientadores podem realizar essa ação.

### Métodos Possíveis
- `POST`: Define a data de vencimento para a etapa atual do projeto.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `projectName` (obrigatório): Nome do projeto.
  - `dueDate` (obrigatório): Data de vencimento no formato "YYYY-MM-DDTHH:mm:ss".

### Possíveis Erros
- **400 Bad Request**: Corpo da requisição inválido.
- **403 Forbidden**: Usuário não autorizado a definir datas de vencimento.
- **404 Not Found**: Projeto não encontrado ou usuário não é orientador do projeto.
- **500 Internal Server Error**: Erro interno ao definir a data de vencimento.

### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/setDueDate -d '{"projectName": "nome_do_projeto", "dueDate": "2023-01-31T15:00:00"}'
```

Respostas de Exemplo

Sucesso (Definição de Data de Vencimento)
```
{
  "msg": "Due date set successfully",
  "success": true
}
```

Erro (Projeto já Concluído)
```
{
  "msg": "Cannot set due date, project is already completed",
  "success": false
}
```