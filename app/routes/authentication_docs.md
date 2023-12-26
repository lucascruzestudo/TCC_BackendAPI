## Endpoint: `/api/v1/register`

### Descrição
Este endpoint é utilizado para registrar um novo usuário na aplicação.

### Métodos Possíveis
- `POST`: Registra um novo usuário.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `username` (obrigatório): Nome de usuário do novo usuário.
  - `password` (obrigatório): Senha do novo usuário.
  - `role` (obrigatório): Função do novo usuário (1 para admin, 2 para coordenador, 3 para orientador, 4 para aluno).
  - `email` (opcional): Endereço de e-mail do novo usuário.
  - `profile_picture` (opcional): URL da foto de perfil do novo usuário.
  - `full_name` (opcional): Nome completo do novo usuário.

### Possíveis Erros
- **400 Bad Request**: Role é obrigatório no corpo da requisição.
- **401 Unauthorized**: Chave de admin inválida para registro de administrador.
- **409 Conflict**: Nome de usuário já existe.

### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/register -d '{"username": "novo_usuario", "password": "senha123", "role": 2, "email": "usuario@email.com"}'
```

Respostas de Exemplo

Sucesso (Criação de Usuário)
```
{
  "msg": "User created successfully"
}
```

Erro (Nome de Usuário Já Existe)
```
{
  "msg": "Username already exists"
}
```

Erro (Role Ausente no Corpo da Requisição)
```
{
  "msg": "Role is required in the request body"
}
```

Erro (Chave de Admin Inválida)
```
{
  "msg": "Invalid admkey for admin registration"
}
```

### Notas Adicionais

O campo role deve ser 1 para admin, 2 para coordenador, 3 para orientador, 4 para aluno.<br/>
Se o campo role for 1 (admin), a chave de admin (AdmKey) deve ser fornecida no cabeçalho da requisição.<br/>
Se o campo email, profile_picture ou full_name não forem fornecidos, serão definidos como vazio por padrão.<br/>

## Endpoint: `/api/v1/login`

### Descrição
Este endpoint é utilizado para realizar o login de um usuário na aplicação.

### Métodos Possíveis
- `POST`: Realiza o login do usuário.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `username` (obrigatório): Nome de usuário do usuário que está realizando o login.
  - `password` (obrigatório): Senha do usuário que está realizando o login.

### Possíveis Erros
- **401 Unauthorized**: O nome de usuário ou a senha estão incorretos.

### Exemplo de Uso
```bash
curl -X POST http://sua-api.com/api/v1/login -d '{"username": "usuario_existente", "password": "senha123"}'
```

Respostas de Exemplo

Sucesso (Login)
```
{
  "access_token": "seu_token_de_acesso",
  "refresh_token": "seu_token_de_atualizacao"
}
```

Erro (Nome de Usuário ou Senha Incorretos)
```
{
  "msg": "The username or password is incorrect"
}
```

### Notas Adicionais

- A autenticação é realizada comparando o nome de usuário e a senha fornecidos com os dados armazenados no banco de dados.
- Em caso de sucesso, são gerados tokens de acesso e atualização para o usuário.

## Endpoint: `/api/v1/refresh`

### Descrição
Este endpoint é utilizado para renovar os tokens de acesso e atualização de um usuário autenticado.

### Métodos Possíveis
- `POST`: Renova os tokens de acesso e atualização.

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de atualização (Refresh Token) fornecido durante o login.

### Possíveis Erros
- **401 Unauthorized**: Token de atualização inválido ou expirado.

### Exemplo de Uso
```bash
curl -X POST -H "Authorization: Bearer seu_refresh_token" http://sua-api.com/api/v1/refresh
```

Respostas de Exemplo

Sucesso (Renovação de Tokens)
```
{
  "access_token": "seu_novo_token_de_acesso",
  "refresh_token": "seu_novo_token_de_atualizacao"
}
```

Erro (Token de Atualização Inválido ou Expirado)
```
{
  "msg": "Invalid or expired refresh token"
}
```

### Notas Adicionais

- O token de atualização (Refresh Token) deve ser incluído no cabeçalho da requisição usando a chave "Authorization".
- Em caso de sucesso, são gerados novos tokens de acesso e atualização para o usuário.
- Caso o token de atualização seja inválido ou tenha expirado, a requisição será negada.