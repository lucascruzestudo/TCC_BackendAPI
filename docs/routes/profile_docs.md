## Endpoint: `/api/v1/profile`

### Descrição
Este endpoint permite visualizar, atualizar e excluir o perfil do usuário autenticado.

### Métodos Possíveis
- `GET`: Recupera as informações do perfil do usuário informado.
- `PUT`: Atualiza as informações do perfil do usuário autenticado.
- `DELETE`: Exclui o perfil do usuário informado (somente para usuários com função de admin ou coordenador).

### Parâmetros
- **Cabeçalho da Requisição**:
  - `Authorization` (obrigatório): Token de acesso.

- **Corpo da Requisição (PUT)**:
  - `email` (opcional): Novo endereço de e-mail.
  - `profile_picture` (opcional): Nova URL da foto de perfil.

### Possíveis Erros
- **401 Unauthorized**: Token de acesso inválido.
- **403 Forbidden**: Usuário não autorizado a realizar a operação.
- **404 Not Found**: Perfil do usuário não encontrado.
- **500 Internal Server Error**: Erro ao gerenciar o perfil do usuário.

### Exemplo de Uso
```bash
# GET (Recupera informações do perfil)
curl -X GET -H "Authorization: Bearer seu_token_de_acesso" http://sua-api.com/api/v1/profile

# PUT (Atualiza informações do perfil)
curl -X PUT -H "Authorization: Bearer seu_token_de_acesso" -d '{"email": "novo_email@email.com", "profile_picture": "nova_url_da_foto"}' http://sua-api.com/api/v1/profile

# DELETE (Exclui perfil do usuário)
curl -X DELETE -H "Authorization: Bearer seu_token_de_acesso" http://sua-api.com/api/v1/profile
```

Respostas de Exemplo

Sucesso (Recuperação de Perfil)
```
{
  "profile": {
    "username": "seu_nome_de_usuario",
    "role": 2,
    "email": "seu_email@email.com",
    "profile_picture": "url_da_sua_foto_de_perfil",
    "full_name": "Seu Nome Completo"
  }
}
```

Sucesso (Atualização de Perfil)
```
{
  "msg": "Profile updated successfully"
}
```

Sucesso (Exclusão de Perfil)
```
{
  "msg": "User deleted successfully"
}
```

Erro (Token de Acesso Inválido)
```
{
  "msg": "Invalid access token"
}
```

Erro (Usuário Não Autorizado)
```
{
  "msg": "Unauthorized to update this profile"
}
```

Erro (Perfil Não Encontrado)
```
{
  "msg": "Profile not found"
}
```

Erro (Erro Interno do Servidor)
```
{
  "msg": "Internal Server Error"
}
```

### Notas Adicionais

- A atualização das informações de perfil é permitida apenas para o próprio usuário autenticado.
- A exclusão de perfil é permitida apenas para usuários com função de admin ou coordenador.