## Endpoint: `/api/v1/register`

### Descrição
Este endpoint é utilizado para registrar um novo usuário na aplicação.

### URL
[POST] /api/v1/register

markdown
Copy code

### Métodos Possíveis
- `POST`: Registra um novo usuário.

### Parâmetros
- **Corpo da Requisição (JSON)**:
  - `username` (obrigatório): Nome de usuário do novo usuário.
  - `password` (obrigatório): Senha do novo usuário.
  - `role` (obrigatório): Função do novo usuário (1 para admin, 2 para usuário padrão).
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

{
  "msg": "User created successfully"
}
Erro (Nome de Usuário Já Existe)

{
  "msg": "Username already exists"
}
Erro (Role Ausente no Corpo da Requisição)

{
  "msg": "Role is required in the request body"
}
Erro (Chave de Admin Inválida)

{
  "msg": "Invalid admkey for admin registration"
}

Notas Adicionais
O campo role deve ser 1 para admin, 2 para coordenador, 3 para orientador, 4 para aluno.
Se o campo role for 1 (admin), a chave de admin (AdmKey) deve ser fornecida no cabeçalho da requisição.
Se o campo email, profile_picture ou full_name não forem fornecidos, serão definidos como vazio por padrão.