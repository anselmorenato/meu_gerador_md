# 📂 Documentação Técnica do Projeto — MD Studio

Este documento serve como o manual oficial de arquitetura, desenvolvimento e design do sistema **MD Studio**. A aplicação foi projetada sob o padrão **Fábrica de Aplicação (Application Factory)** com controle de dados via repositório em banco SQLite e interface offline otimizada.

---

## 🛠️ 1. Arquitetura Geral & Estrutura de Pastas

O projeto adota uma variação simplificada e modular do padrão MVC (Model-View-Controller) dividido em Blueprints para garantir manutenibilidade:

```text
meu_gerador_md/
├── dados.db              # Banco de dados SQLite relacional
├── documentos/           # Repositório físico de arquivos .md (Sempre a última versão)
├── static/               # Ativos estáticos 100% offline (CSS, JS, Imagens, Fontes)
├── templates/            # Telas da estrutura (HTML estrutural estendido)
├── app.py                # Ponto de entrada (Entrypoint) do servidor Flask
└── src/                  # Código fonte do núcleo da aplicação
    ├── __init__.py       # Inicializador / Fábrica do aplicativo Flask
    ├── rotas.py          # Controlador (Controllers) de rotas HTTP
    └── repositorio.py    # Modelo de dados e abstração do SQLite
```

---

## 🗄️ 2. Camada de Dados: `src/repositorio.py`

A classe `MarkdownRepository` encapsula todas as transações de leitura, escrita, versionamento estrutural e exclusão lógica/física.

### 📝 Mapa de Métodos

| Método | Tipo | Retorno | Descrição |
| :--- | :--- | :--- | :--- |
| `_get_conexao()` | Privado | `sqlite3.Connection` | Abre e retorna uma conexão ativa com o arquivo `dados.db` usando mapeamento `Row`. |
| `_criar_tabelas()` | Privado | `None` | Método disparado na inicialização. Executa o DDL de criação das tabelas `documentos_meta` e `documentos_versoes`. |
| `listar_todos(busca)` | Público | `list[dict]` | Retorna todos os metadados dos arquivos. Se um parâmetro for passado, filtra por título ou conteúdo bruto interno. |
| `obter_meta(filename)` | Público | `dict` \| `None` | Busca os metadados cadastrados de um arquivo físico específico através do nome dele. |
| `listar_versoes(filename)`| Público | `list[dict]` | Retorna o ID, número da versão e data de gravação do histórico de auditoria de um arquivo. |
| `obter_conteudo_versao(f, v)`| Público| `str` | Retorna o texto bruto de uma versão específica `v` do banco. Se `v` for omitido, busca o arquivo físico atual. |
| `salvar(f, cont, tit, up)` | Público | `str` | **Núcleo de Escrita**: Grava o `.md` físico em disco, sobe o contador de versão, atualiza o metadado principal e gera o histórico. |
| `deletar(filename)` | Público | `bool` | Remove o arquivo físico da pasta `documentos/` e expurga os dados das duas tabelas de forma definitiva. |
| `converter_para_html(raw)`| Público | `str` | Recebe o Markdown cru e o compila em tags HTML com suporte a `tables`, `emoji`, `tasklist` e `superfences`. |

---

## 🎛️ 3. Camada de Controle: `src/rotas.py`

As requisições HTTP do navegador são gerenciadas através do Blueprint principal `main`.

### 🧭 Engenharia de Rotas e Endpoints

#### 🏠 Painel Inicial (Home Dashboard)
- **Endpoint**: `/`
- **Nome Técnico**: `main.home`
- **Método**: `GET`
- **Operação**: Captura o parâmetro de query opcional `busca`. Instancia a lista de documentos e injeta na tela `home.html`.

#### 👁️ Modo de Leitura Otimizado (Viewer)
- **Endpoint**: `/visualizar/<filename>`
- **Nome Técnico**: `main.visualizar`
- **Método**: `GET`
- **Operação**: Carrega os metadados e o histórico de versões. Aceita o parâmetro opcional `?v=X`. Se fornecido, lê a versão histórica do banco, senão entrega o HTML final compilado da última versão estável.

#### 📝 Criação de Documentos
- **Endpoint**: `/criar`
- **Nome Técnico**: `main.criar`
- **Métodos**: `GET` \| `POST`
- **Operação**:
  - `GET`: Abre o formulário vazio do editor.
  - `POST`: Coleta o título descritivo do formulário, normaliza-o substituindo espaços por sublinhados (`_`), adiciona a extensão `.md` e chama a gravação como nova entidade (Versão 1).

#### ✏️ Edição Avançada
- **Endpoint**: `/editar/<filename>`
- **Nome Técnico**: `main.editar`
- **Métodos**: `GET` \| `POST`
- **Operação**:
  - `GET`: Puxa a versão mais atual do conteúdo em Markdown e a injeta dentro da área de texto manipulada pelo `EasyMDE`.
  - `POST`: Coleta as edições textuais enviadas, altera os metadados do documento mantendo o nome do arquivo técnico estável e incrementa o controle de versão.

#### 🗑️ Exclusão Absoluta
- **Endpoint**: `/deletar/<filename>`
- **Nome Técnico**: `main.deletar`
- **Método**: `GET`
- **Operação**: Aciona a limpeza lógica e física do arquivo, emitindo uma mensagem flash do Flask de categoria `warning` que desparece automaticamente.

---

## 🗄️ 4. Modelagem do Banco de Dados (SQLite)

O sistema de versionamento é sustentado por um relacionamento de um para muitos (`1:N`) mapeado puramente por consultas SQL preparadas nativas.

### 📊 Diagrama Lógico de Tabelas

```text
  [documentos_meta]                    [documentos_versoes]
  +------------------+                 +--------------------+

  | id (PK)          |                 | id (PK)            |
  | arquivo_nome     |<===============-| arquivo_nome (FK)  |
  | titulo_exibicao  |                 | versao_numero      |
  | versions_count   |                 | conteudo           |
  | criado_em        |                 | salvo_em           |
  | atualizado_em    |                 +--------------------+
  +------------------+
```

---

## 🎨 5. Guias e Tokens de Design do Front-End

O visual do MD Studio foi desenhado usando um **esquema de cores híbrido focado em acessibilidade** (redução de fadiga ocular), acoplado ao framework CSS Bootstrap 5 e componentes dinâmicos em JavaScript.

### 🎨 Paleta de Cores e Variáveis Globais CSS (`:root`)

Toda a identidade visual é gerenciada dinamicamente pelo arquivo `static/css/custom.css` através dos seguintes tokens de design:

- **Fundo Principal (`--bg-main` - `#121824`)**: Cinza-azulado fosco que absorve reflexos nocivos das telas.
- **Painéis e Blocos (`--bg-card` - `#1c2333`)**: Cor de destaque de cartões e áreas internas, criando sensação de relevo e profundidade.
- **Texto Primário (`--text-main` - `#e2e8f0`)**: Tom esbranquiçado suave de alto contraste contra o fundo escuro, reduzindo o cansaço na leitura continuada.
- **Cor de Destaque (`--accent` - `#38bdf8`)**: Azul Sky vibrante utilizado cirurgicamente em links importantes, ícones e botões de ação primários.

### 📝 Engenharia Visual do Editor Avançado (`EasyMDE`)

O editor de texto foi forçado a sobrescrever seus estilos nativos do Bootstrap para entregar a sensação de ambiente de programação focado:
- **Fontes**: Uso de fontes monoespaçadas estáveis (`Fira Code` / `ui-monospace`) para perfeita identificação de caracteres especiais de programação.
- **Espaçamento Cirúrgico**: A linha do editor foi reduzida a um padding de `1px 8px` e `line-height: 1.5`, resolvendo quebras de linha fantasmas no motor CodeMirror.
- **Identificação Automática de Linguagem**: Graças ao CSS dinâmico estruturado via seletor `:has()`, blocos delimitados por crases (como ` ```python ` ou ` ```sql `) renderizam dinamicamente um cabeçalho flutuante customizado com o nome e o ícone do interpretador correspondente sem precisar rodar JS adicional.

### 🔍 Script de Pesquisa Interna

Inserido no arquivo `templates/visualizar.html`, o mecanismo varre os nós de texto (Node 3) de forma recursiva. Ele ignora tags funcionais (`<pre>`, `<code>`, `<script>`) e envolve as ocorrências pesquisadas em tempo real sob a classe `mark.realce-busca`, o que evita a corrupção do layout original do documento compilado.
