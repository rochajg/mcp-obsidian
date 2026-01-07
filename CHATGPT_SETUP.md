# Configuração do ChatGPT Custom GPT com Obsidian MCP

O ChatGPT Custom GPT tem limitações com o protocolo MCP sobre SSE. A solução é usar **Custom Actions** com a REST API do servidor.

## ✅ Solução: Custom Actions (REST API)

### Passo 1: Criar Custom GPT

1. Acesse: https://chat.openai.com/gpts/editor
2. Clique em **"Create a GPT"**

### Passo 2: Configurar Básico

**Name:**
```
Obsidian Vault Manager
```

**Description:**
```
Manages your Obsidian vault - reads, searches, creates, and updates notes.
```

**Instructions:**
```
You are an assistant that helps manage an Obsidian vault. You have access to tools to:
- List files in the vault
- Read file contents
- Search for content
- Create new notes
- Update existing notes
- Append content to notes
- Delete files

When the user asks to:
- "Show me my notes" → use obsidian_list_files_in_vault
- "Read [file]" → use obsidian_get_file_contents
- "Find notes about [topic]" → use obsidian_simple_search or obsidian_complex_search
- "Create a note about [topic]" → use obsidian_put_content
- "Add [text] to [file]" → use obsidian_append_content
- "Update [file]" → use obsidian_patch_content or obsidian_put_content
- "Delete [file]" → use obsidian_delete_file

Always use the tools to interact with the vault. Never make up file names or content.
```

### Passo 3: Configurar Actions

1. Na seção **"Actions"**, clique em **"Create new action"**
2. Escolha **"Import from URL"**
3. Cole a URL do schema OpenAPI:
   ```
   https://obsidian-api.rochajg.dev:443/openapi-mcp-http.yaml
   ```
   
   **OU** copie o conteúdo do arquivo `openapi-mcp-http.yaml` e cole diretamente

### Passo 4: Configurar Autenticação

1. Em **"Authentication"**, selecione: **Bearer**
2. **API Key**: Cole seu `MCP_HTTP_API_KEY`
3. **Auth Type**: `Bearer`

### Passo 5: Testar

Clique em **"Test"** e experimente:

**Exemplo 1: Listar arquivos**
```json
{
  "name": "obsidian_list_files_in_vault",
  "arguments": {}
}
```

**Exemplo 2: Criar nota**
```json
{
  "name": "obsidian_put_content",
  "arguments": {
    "filepath": "Test/chatgpt-test.md",
    "content": "# Test Note\n\nCreated by ChatGPT!"
  }
}
```

### Passo 6: Salvar

Clique em **"Save"** e depois **"Publish"** (pode escolher "Only me" para manter privado)

## 🎯 Ferramentas Disponíveis

O GPT terá acesso a estas ferramentas via `/tools/call`:

### 1. **obsidian_list_files_in_vault**
Lista todos os arquivos do vault
```json
{"name": "obsidian_list_files_in_vault", "arguments": {}}
```

### 2. **obsidian_list_files_in_dir**
Lista arquivos em um diretório específico
```json
{
  "name": "obsidian_list_files_in_dir",
  "arguments": {"dirpath": "Projects"}
}
```

### 3. **obsidian_get_file_contents**
Lê o conteúdo de um arquivo
```json
{
  "name": "obsidian_get_file_contents",
  "arguments": {"filepath": "Daily/2024-01-06.md"}
}
```

### 4. **obsidian_simple_search**
Busca simples por texto
```json
{
  "name": "obsidian_simple_search",
  "arguments": {
    "query": "meeting notes",
    "contextLength": 100
  }
}
```

### 5. **obsidian_complex_search**
Busca avançada com filtros
```json
{
  "name": "obsidian_complex_search",
  "arguments": {
    "query": "project",
    "contextLength": 100
  }
}
```

### 6. **obsidian_put_content**
Cria ou substitui arquivo completamente
```json
{
  "name": "obsidian_put_content",
  "arguments": {
    "filepath": "Notes/new-note.md",
    "content": "# New Note\n\nContent here..."
  }
}
```

### 7. **obsidian_append_content**
Adiciona conteúdo ao final do arquivo
```json
{
  "name": "obsidian_append_content",
  "arguments": {
    "filepath": "Daily/today.md",
    "content": "\n- New task"
  }
}
```

### 8. **obsidian_patch_content**
Atualiza seções específicas do arquivo
```json
{
  "name": "obsidian_patch_content",
  "arguments": {
    "filepath": "Projects/project.md",
    "content": "## Updated Section\n\nNew content"
  }
}
```

### 9. **obsidian_delete_file**
Deleta um arquivo
```json
{
  "name": "obsidian_delete_file",
  "arguments": {"filepath": "Temp/old.md"}
}
```

## 🧪 Exemplos de Uso com o GPT

Depois de configurado, você pode conversar naturalmente:

**Você:** "Liste todos os meus arquivos"
→ GPT usa `obsidian_list_files_in_vault`

**Você:** "Crie uma nota sobre a reunião de hoje"
→ GPT usa `obsidian_put_content` com filepath `Daily/2024-01-06.md`

**Você:** "Procure minhas notas sobre projetos"
→ GPT usa `obsidian_simple_search` com query "projetos"

**Você:** "Adicione uma tarefa ao meu diário de hoje"
→ GPT usa `obsidian_append_content`

**Você:** "Leia o arquivo Projects/website.md"
→ GPT usa `obsidian_get_file_contents`

## 🔒 Segurança

- ✅ Usa Bearer Token authentication
- ✅ HTTPS obrigatório
- ✅ API key nunca exposta ao usuário final
- ✅ Apenas você tem acesso ao Custom GPT (se publicar como "Only me")

## 🐛 Troubleshooting

### Erro 401 Unauthorized
- Verifique se o API Key está correto
- Confirme que `MCP_HTTP_API_KEY` está definido no servidor

### Erro 404 Not Found
- Verifique se o servidor está rodando
- Confirme a URL: `https://obsidian-api.rochajg.dev:443`

### GPT não chama as ferramentas
- Revise as "Instructions" do GPT
- Seja específico nos comandos: "Use a ferramenta X para..."

### Servidor não responde
```bash
# Verifique o status do container
docker ps

# Veja os logs
docker logs -f CONTAINER_ID
```

## 📚 Mais Informações

- REST API endpoints: `/tools` e `/tools/call`
- OpenAPI schema: `openapi-mcp-http.yaml`
- Documentação completa: `README.md`
