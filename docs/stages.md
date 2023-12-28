### Endpoint: `/api/v1/stages/approve`

#### Descrição
Este endpoint é utilizado para aprovar a etapa atual de um projeto. Apenas orientadores podem utilizar este endpoint.

#### Métodos Possíveis
- `POST`: Aprova a etapa atual do projeto.

#### Parâmetros
- **Cabeçalho (JWT)**: Deve conter um token JWT válido do orientador.
- **Corpo da Requisição (JSON)**:
  - `Nenhum parâmetro necessário`.

#### Possíveis Erros
- **400 Bad Request**: Etapa atual inválida ou não encontrada no projeto.
- **403 Forbidden**: Usuário não autorizado a aprovar etapas.
- **404 Not Found**: Projeto não encontrado ou orientador não é o orientador do projeto.
- **500 Internal Server Error**: Erro interno ao aprovar a etapa.

#### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/approve
```

Respostas de Exemplo

Sucesso (Etapa Aprovada)
```json
{
  "msg": "Stage approved successfully",
  "success": true
}
```

Erro (Etapa Atual Inválida)
```json
{
  "msg": "Invalid current stage ID or the stage is not found in the project",
  "success": false
}
```

Erro (Usuário Não Autorizado)
```json
{
  "msg": "Unauthorized to approve stages",
  "success": false
}
```

---

### Endpoint: `/api/v1/stages/revert`

#### Descrição
Este endpoint é utilizado para reverter a etapa atual de um projeto. Apenas orientadores podem utilizar este endpoint.

#### Métodos Possíveis
- `POST`: Reverte a etapa atual do projeto para a etapa anterior.

#### Parâmetros
- **Cabeçalho (JWT)**: Deve conter um token JWT válido do orientador.
- **Corpo da Requisição (JSON)**:
  - `projectName` (obrigatório): Nome do projeto para o qual reverter a etapa.

#### Possíveis Erros
- **400 Bad Request**: Nome do projeto não fornecido ou inválido.
- **403 Forbidden**: Usuário não autorizado a reverter etapas.
- **404 Not Found**: Projeto não encontrado ou orientador não é o orientador do projeto.
- **500 Internal Server Error**: Erro interno ao reverter a etapa.

#### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/revert -d '{"projectName": "NomeProjeto"}'
```

Respostas de Exemplo

Sucesso (Etapa Revertida)
```json
{
  "msg": "Stage reverted successfully",
  "success": true
}
```

Erro (Projeto Não Encontrado)
```json
{
  "msg": "Project not found or you are not the advisor for this project",
  "success": false
}
```

Erro (Usuário Não Autorizado)
```json
{
  "msg": "Unauthorized to revert stages",
  "success": false
}
```

---

### Endpoint: `/api/v1/stages/setDueDate`

#### Descrição
Este endpoint é utilizado para definir a data de vencimento para a etapa atual de um projeto. Apenas orientadores podem utilizar este endpoint.

#### Métodos Possíveis
- `POST`: Define a data de vencimento para a etapa atual do projeto.

#### Parâmetros
- **Cabeçalho (JWT)**: Deve conter um token JWT válido do orientador.
- **Corpo da Requisição (JSON)**:
  - `projectName` (obrigatório): Nome do projeto para o qual definir a data de vencimento.
  - `dueDate` (obrigatório): Data de vencimento no formato ISO 8601 (ex: "2023-12-31T23:59:59").

#### Possíveis Erros
- **400 Bad Request**: Nome do projeto ou data de vencimento não fornecidos ou inválidos.
- **403 Forbidden**: Usuário não autorizado a definir a data de vencimento.
- **404 Not Found**: Projeto não encontrado ou orientador não é o orientador do projeto.
- **500 Internal Server Error**: Erro interno ao definir a data de vencimento.

#### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/stages/setDueDate -d '{"projectName": "NomeProjeto", "dueDate": "2023-12-31T23:59:59"}'
```

Respostas de Exemplo

Sucesso (Data de Vencimento Definida)
```json
{
  "msg": "Due date set successfully",
  "success": true
}
```

Erro (Projeto Não Encontrado)
```json
{
  "msg": "Project not found or you are not the advisor for this project",
  "success": false
}
```

Erro (Usuário Não Autorizado)
```json
{
  "msg": "Unauthorized to set due date",
  "success": false
}
```

