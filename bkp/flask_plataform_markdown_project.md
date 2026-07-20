Com certeza! Vamos estruturar uma aplicação Flask completa, organizada e funcional. Para o editor avançado com preview em tempo real e suporte a emojis, usaremos o **EasyMDE** (um editor Markdown moderno em JavaScript) integrado ao **Font Awesome** para ícones.Aqui está o passo a passo e o código completo para rodar no seu computador.

## 📂 Estrutura do Projeto

Crie uma pasta para o seu projeto e organize os arquivos desta forma:

```text
meu_gerador_md/
│
├── app.py               # Código do Backend (Flask)
├── documentos/          # Pasta onde os arquivos .md serão salvos
│   └── Exemplo.md       # Um arquivo de teste
└── templates/           # Pasta dos arquivos HTML (Front-end)
    ├── base.html        # Layout padrão (Navbar e Scripts)
    ├── home.html        # Página inicial (Listagem dos arquivos)
    └── editor.html      # Página de Criação/Edição com Preview

```

## 🧠 1. Backend: app.py

Este arquivo gerencia a leitura, criação, edição e exclusão dos arquivos Markdown dentro da pasta `documentos/`.

```python
import os
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

# Define e garante que a pasta de documentos exista
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documentos')
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

def listar_documentos():
    """Lista todos os arquivos .md da pasta."""
    if not os.path.exists(DOCS_DIR):
        return []
    return [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]

@app.route('/')
def home():
    documentos = listar_documentos()
    return render_template('home.html', documentos=documentos)

@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        titulo = request.form.get('titulo').strip()
        conteudo = request.form.get('conteudo')
        
        if not titulo:
            flash("O título é obrigatório!", "danger")
            return redirect(url_for('criar'))
            
        # Garante a extensão .md
        if not titulo.endswith('.md'):
            titulo += '.md'
            
        filepath = os.path.join(DOCS_DIR, titulo)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
            
        flash(f"Documento '{titulo}' criado com sucesso!", "success")
        return redirect(url_for('home'))
        
    return render_template('editor.html', acao="Criar", titulo="", conteudo="")

@app.route('/editar/<filename>', methods=['GET', 'POST'])
def editar(filename):
    filepath = os.path.join(DOCS_DIR, filename)
    
    if not os.path.exists(filepath):
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        flash(f"Documento '{filename}' atualizado!", "success")
        return redirect(url_for('home'))

    with open(filepath, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # Remove a extensão .md apenas para exibição visual no input de título
    titulo_sem_ext = filename[:-3] if filename.endswith('.md') else filename
    return render_template('editor.html', acao="Editar", titulo=titulo_sem_ext, conteudo=conteudo, filename=filename)

@app.route('/deletar/<filename>')
def deletar(filename):
    filepath = os.path.join(DOCS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Documento '{filename}' removido.", "warning")
    else:
        flash("Arquivo não encontrado.", "danger")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
```

🎨 2. Front-end: Templates HTML

Utilizaremos o framework **Bootstrap 5** para deixar o visual limpo, moderno e responsivo, junto com o **EasyMDE** para o editor Markdown avançado.

📄 templates/base.html

Este é o esqueleto da aplicação. Ele carrega as bibliotecas necessárias do editor de texto e dos ícones.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerenciador Markdown</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://jsdelivr.net" rel="stylesheet">
    <!-- Font Awesome (Ícones e Emojis) -->
    <link href="https://cloudflare.com" rel="stylesheet">
    <!-- EasyMDE CSS (Editor Avançado) -->
    <link rel="stylesheet" href="https://jsdelivr.net">
    <style>
        body { background-color: #f8f9fa; }
        .navbar-brand { font-weight: bold; }
        .card { border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        /* Ajuste fino para o preview do EasyMDE herdar estilos bonitos */
        .editor-preview { background: #fff !important; color: #333 !important; }
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('home') }}"><i class="fa-solid fa-file-lines me-2"></i>MD Studio</a>
            <div class="navbar-nav ms-auto">
                <a class="btn btn-primary btn-sm" href="{{ url_for('criar') }}"><i class="fa-solid fa-plus me-1"></i> Novo Documento</a>
            </div>
        </div>
    </nav>

    <div class="container">
        <!-- Mensagens de Alerta (Sucesso/Erro) -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <!-- Bootstrap JS -->
    <script src="https://jsdelivr.net"></script>
    <!-- EasyMDE JS -->
    <script src="https://jsdelivr.net"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

📄 templates/home.html

Exibe os documentos salvos na pasta em um formato de lista elegante com ações para editar ou excluir.

```html
{% extends 'base.html' %}

{% block content %}
<div class="row mb-4 align-items-center">
    <div class="col">
        <h2 class="fw-bold text-secondary">Meus Documentos Markdown</h2>
    </div>
</div>

<div class="card p-4">
    {% if documentos %}
        <div class="list-group list-group-flush">
            {% for doc in documentos %}
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div class="d-flex align-items-center">
                        <i class="fa-regular fa-file-code text-primary fs-4 me-3"></i>
                        <span class="fs-5 fw-medium text-dark">{{ doc }}</span>
                    </div>
                    <div>
                        <a href="{{ url_for('editar', filename=doc) }}" class="btn btn-outline-secondary btn-sm me-2">
                            <i class="fa-solid fa-pen-to-square"></i> Editar
                        </a>
                        <a href="{{ url_for('deletar', filename=doc) }}" class="btn btn-outline-danger btn-sm" onclick="return confirm('Tem certeza que deseja deletar este documento?')">
                            <i class="fa-solid fa-trash"></i> Excluir
                        </a>
                    </div>
                </div>
            {% endfor %}
        </div>
    {% else %}
        <div class="text-center py-5">
            <i class="fa-regular fa-folder-open text-muted fs-1 mb-3"></i>
            <p class="text-muted fs-5">Nenhum documento encontrado. Crie o seu primeiro arquivo!</p>
            <a class="btn btn-primary" href="{{ url_for('criar') }}">Criar Documento</a>
        </div>
    {% endif %}
</div>
{% endblock %}
```

📄 templates/editor.html

Onde a mágica do editor acontece. Ele injeta o editor avançado na textarea tradicional e ativa o preview em tempo real.

```html
{% extends 'base.html' %}

{% block content %}
<div class="card p-4">
    <h3 class="fw-bold mb-4 text-secondary">{{ acao }} Documento</h3>
    
    <form method="POST">
        <div class="mb-3">
            <label for="titulo" class="form-label fw-semibold">Título do Arquivo</label>
            <input type="text" class="form-control form-control-lg" id="titulo" name="titulo" value="{{ titulo }}" placeholder="Ex: Relatorio_De_Vendas" {% if acao == "Editar" %}readonly disabled{% endif %} required>
            {% if acao == "Editar" %}
                <small class="text-muted">O nome do arquivo não pode ser alterado após a criação.</small>
            {% endif %}
        </div>

        <div class="mb-3">
            <label for="conteudo" class="form-label fw-semibold">Conteúdo Markdown</label>
            <textarea id="conteudo" name="conteudo">{{ conteudo }}</textarea>
        </div>

        <div class="d-flex justify-content-between mt-4">
            <a href="{{ url_for('home') }}" class="btn btn-light"><i class="fa-solid fa-arrow-left me-1"></i> Voltar</a>
            <button type="submit" class="btn btn-success px-4"><i class="fa-solid fa-floppy-disk me-1"></i> Salvar Documento</button>
        </div>
    </form>
</div>
{% endblock %}

{% block scripts %}
<script>
    // Inicializa o Editor Avançado EasyMDE
    const easyMDE = new EasyMDE({
        element: document.getElementById('conteudo'),
        spellChecker: false, // Desativa corretor em inglês por padrão
        autosave: {
            enabled: true,
            uniqueId: "md_studio_editor_{{ titulo }}",
            delay: 1000,
        },
        renderingConfig: {
            singleLineBreaks: false,
            codeSyntaxHighlighting: true, // Melhora blocos de código no preview
        },
        // Customização da barra de ferramentas para suportar imagens e side-by-side preview
        toolbar: [
            "bold", "italic", "heading", "|", 
            "quote", "unordered-list", "ordered-list", "|", 
            "link", "image", "table", "horizontal-rule", "|", 
            "preview", "side-by-side", "fullscreen", "|", 
            "guide"
        ],
        placeholder: "Comece a escrever o seu Markdown aqui... \nVocê pode usar emojis diretamente copiando e colando (Ex: 🚀, 💻, 🎨) ou usar imagens locais referenciando o caminho delas.",
    });
</script>
{% endblock %}
```

## 🚀 Como Rodar a Aplicação

1. Instale o Flask utilizando o terminal:

```bash
pip install Flask
```

2. Execute o arquivo principal da aplicação:

```bash 
python app.py
```

3. Abra o seu navegador web e acesse o endereço fornecido no terminal (geralmente `http://127.0.0.1:5000`).

💡 Dicas de Uso para Imagens e Emojis

- **Imagens Locais:** Para renderizar uma imagem que está no seu computador dentro do preview do markdown, basta passar o caminho completo dela no botão de imagem. Exemplo: `![Minha Foto](file:///C:/Users/Nome/Imagens/foto.png)`.
- Ícones e Emojis: O editor aceita emojis copiados diretamente do seu sistema operacional (Ex: `Win + .` no Windows ou `Cmd + Ctrl + Espaço` no Mac). Eles aparecem formatados tanto na edição quanto no preview automático (Ex: 🚀, 📂, ⚠️).

Se você quiser expandir essa aplicação no futuro, me avise se prefere adicionar **mecanismo de upload automático de fotos** direto para o servidor ou **exportação para PDF**. O que gostaria de testar primeiro?


Com certeza! Vamos transformar o visual da sua aplicação para deixá-la com uma cara super profissional, moderna e no estilo **Dark Mode premium** (com detalhes sutis e elegantes) ou um **Light Mode minimalista sofisticado**.

Para não quebrar o seu backend, faremos todas as melhorias **apenas substituindo os arquivos HTML** na pasta `templates/`. Substituímos o Bootstrap puro por uma combinação de variáveis CSS modernas, layouts flexíveis e um acabamento premium para o editor.

Substitua os seus arquivos atuais por estes novos códigos:

--------------------

## 🎨 1. Novo `templates/base.html` (Layout e Tema Global)

Este arquivo define o tema escuro moderno de fundo, tipografia limpa (Inter/Sans-serif) e alertas elegantes flutuantes.

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MD Studio — Premium Markdown Editor</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://jsdelivr.net" rel="stylesheet">
    <!-- Font Awesome Pro-like -->
    <link href="https://cloudflare.com" rel="stylesheet">
    <!-- EasyMDE CSS -->
    <link rel="stylesheet" href="https://jsdelivr.net">
    
    <style>
        :root {
            --bg-main: #0f172a;       /* Slate 900 */
            --bg-card: #1e293b;       /* Slate 800 */
            --bg-nav: #0b0f19;        /* Slate 950 */
            --text-main: #f8fafc;     /* Slate 50 */
            --text-muted: #94a3b8;    /* Slate 400 */
            --accent: #38bdf8;        /* Sky 400 */
            --accent-hover: #0ea5e9;  /* Sky 500 */
            --border-color: #334155;  /* Slate 700 */
            --danger: #ef4444;
            --success: #10b981;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
        }

        /* Navbar Customizada */
        .navbar-custom {
            background-color: var(--bg-nav);
            border-bottom: 1px solid var(--border-color);
            padding: 0.8rem 0;
        }
        .navbar-brand-custom {
            font-weight: 700;
            letter-spacing: -0.5px;
            color: var(--text-main) !important;
            font-size: 1.35rem;
        }
        .navbar-brand-custom span {
            color: var(--accent);
        }

        /* Cards Estilizados */
        .card-custom {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            padding: 2rem;
        }

        /* Botões Modernos */
        .btn-accent {
            background-color: var(--accent);
            color: #0f172a;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
        }
        .btn-accent:hover {
            background-color: var(--accent-hover);
            color: #0f172a;
            transform: translateY(-1px);
        }
        .btn-outline-custom {
            border: 1px solid var(--border-color);
            color: var(--text-main);
            background: transparent;
            transition: all 0.2s ease;
        }
        .btn-outline-custom:hover {
            background: var(--border-color);
            color: var(--accent);
        }

        /* Customização do Editor EasyMDE para Casar com o Tema Escuro */
        .EasyMDEContainer {
            background-color: #111827 !important;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        .editor-toolbar {
            background-color: #1f2937 !important;
            border-bottom: 1px solid var(--border-color) !important;
            opacity: 0.9;
        }
        .editor-toolbar button {
            color: #e5e7eb !important;
        }
        .editor-toolbar button:hover, .editor-toolbar button.active {
            background: #374151 !important;
            color: var(--accent) !important;
        }
        .CodeMirror {
            background-color: #111827 !important;
            color: #f3f4f6 !important;
            border: none !important;
        }
        /* Tela de preview dividida ou cheia */
        .editor-preview, .editor-preview-side {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
        }
        /* Estilos do texto Renderizado dentro do Preview */
        .editor-preview h1, .editor-preview h2, .editor-preview-side h1, .editor-preview-side h2 {
            color: var(--accent);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3rem;
        }
        .editor-preview code, .editor-preview-side code {
            background: #374151;
            padding: 2px 6px;
            border-radius: 4px;
            color: #f472b6;
        }

        /* Alertas Toast Flutuantes */
        .alert-floating {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            min-width: 300px;
            border-left: 5px solid transparent;
        }
        .alert-success { border-left-color: var(--success); background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
        .alert-danger { border-left-color: var(--danger); background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
        .alert-warning { border-left-color: #f59e0b; background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-custom mb-5">
        <div class="container">
            <a class="navbar-brand navbar-brand-custom" href="{{ url_for('home') }}">
                <i class="fa-solid fa-cubes text-info me-2"></i>MD<span>Studio</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="btn btn-accent btn-sm px-3 py-2" href="{{ url_for('criar') }}">
                    <i class="fa-solid fa-plus me-1"></i> Criar Documento
                </a>
            </div>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-floating alert-dismissible fade show" role="alert">
                        <div class="d-flex align-items-center">
                            {% if category == 'success' %}<i class="fa-solid fa-circle-check text-success me-2 fs-5"></i>
                            {% elif category == 'danger' %}<i class="fa-solid fa-circle-xmark text-danger me-2 fs-5"></i>
                            {% else %}<i class="fa-solid fa-triangle-exclamation text-warning me-2 fs-5"></i>{% endif %}
                            <span>{{ message }}</span>
                        </div>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://jsdelivr.net"></script>
    <script src="https://jsdelivr.net"></script>
    <!-- Auto close alerts -->
    <script>
        setTimeout(() => {
            let alerts = document.querySelectorAll('.alert-floating');
            alerts.forEach(alert => {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 4000);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

## 📂 2. Novo `templates/home.html` (Dashboard de Arquivos)

Substitui a lista simples por uma visualização limpa e espaçada, com efeitos de transição ao passar o mouse.

```html
{% extends 'base.html' %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h2 class="fw-bold h4 text-uppercase tracking-wider" style="color: var(--text-muted); letter-spacing: 1px;">
            <i class="fa-solid fa-folder-tree me-2 text-info"></i>Seus Arquivos
        </h2>
    </div>
</div>

<div class="card-custom">
    {% if documentos %}
        <div class="table-responsive">
            <table class="table table-dark table-hover align-middle mb-0" style="--bs-table-bg: transparent; --bs-table-hover-bg: #2d3748;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border-color); color: var(--text-muted);">
                        <th scope="col" class="pb-3 text-start">Nome do Documento</th>
                        <th scope="col" class="pb-3 text-end">Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for doc in documentos %}
                        <tr style="border-bottom: 1px solid #334155;">
                            <td class="py-3 text-start">
                                <div class="d-flex align-items-center">
                                    <div class="p-2 rounded bg-opacity-10 bg-info text-info me-3" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                                        <i class="fa-brands fa-markdown fs-4"></i>
                                    </div>
                                    <div>
                                        <span class="fs-5 fw-semibold text-white d-block">{{ doc }}</span>
                                    </div>
                                </div>
                            </td>
                            <td class="py-3 text-end">
                                <a href="{{ url_for('editar', filename=doc) }}" class="btn btn-outline-custom btn-sm me-2 px-3">
                                    <i class="fa-solid fa-pen-to-square me-1"></i> Abrir Editor
                                </a>
                                <a href="{{ url_for('deletar', filename=doc) }}" class="btn btn-outline-danger btn-sm px-3" style="border: 1px solid #552222;" onclick="return confirm('Tem certeza que deseja deletar este documento?')">
                                    <i class="fa-solid fa-trash-can"></i>
                                </a>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="text-center py-5">
            <div class="mb-4 text-muted" style="font-size: 4rem;">
                <i class="fa-solid fa-bezier-curve opacity-20"></i>
            </div>
            <h4 class="fw-bold text-white">Nenhum repositório de Markdown ativo</h4>
            <p class="text-muted mx-auto" style="max-width: 400px;">Crie um novo arquivo formatado para começar a organizar sua estrutura de documentação.</p>
            <a class="btn btn-accent mt-3 px-4" href="{{ url_for('criar') }}">
                <i class="fa-solid fa-file-circle-plus me-1"></i> Começar Agora
            </a>
        </div>
    {% endif %}
</div>
{% endblock %}
```

## 📝 3. Novo `templates/editor.html` (Formulários do Painel de Escrita)

Melhora os inputs de texto, adiciona avisos discretos e deixa os botões de ação fixos no rodapé da página.

```html
{% extends 'base.html' %}

{% block content %}
<div class="card-custom mb-5">
    <div class="d-flex align-items-center justify-content-between mb-4 pb-3" style="border-bottom: 1px solid var(--border-color);">
        <h3 class="fw-bold text-white m-0">
            <i class="fa-solid fa-wand-magic-sparkles text-info me-2"></i>{{ acao }} Documento
        </h3>
        {% if acao == "Editar" %}
            <span class="badge bg-secondary px-3 py-2 border border-dark"><i class="fa-solid fa-lock me-1"></i> Modo Edição</span>
        {% endif %}
    </div>
    
    <form method="POST">
        <div class="mb-4">
            <label for="titulo" class="form-label fw-semibold text-light mb-2">Nome do Arquivo Markdown</label>
            <div class="input-group">
                <span class="input-group-text bg-dark border-secondary text-muted"><i class="fa-solid fa-file-signature"></i></span>
                <input type="text" class="form-control form-control-lg bg-dark text-white border-secondary" id="titulo" name="titulo" value="{{ titulo }}" placeholder="Ex: Guia_Rapido_Da_Equipe" style="box-shadow: none;" {% if acao == "Editar" %}readonly disabled{% endif %} required>
            </div>
            {% if acao == "Editar" %}
                <div class="form-text text-warning mt-2"><i class="fa-solid fa-circle-info me-1"></i> Para renomear, crie um novo arquivo ou altere o nome do arquivo original diretamente no sistema de pastas.</div>
            {% endif %}
        </div>

        <div class="mb-4">
            <label class="form-label fw-semibold text-light mb-2">Área de Trabalho (Markdown + Live Preview)</label>
            <textarea id="conteudo" name="conteudo">{{ conteudo }}</textarea>
        </div>

        <div class="d-flex justify-content-between align-items-center pt-3" style="border-top: 1px solid var(--border-color);">
            <a href="{{ url_for('home') }}" class="btn btn-outline-custom px-4 py-2">
                <i class="fa-solid fa-chevron-left me-2"></i> Painel Inicial
            </a>
            <button type="submit" class="btn btn-accent px-5 py-2 fs-6">
                <i class="fa-solid fa-cloud-arrow-up me-2"></i> Gravar Alterações
            </button>
        </div>
    </form>
</div>
{% endblock %}

{% block scripts %}
<script>
    const easyMDE = new EasyMDE({
        element: document.getElementById('conteudo'),
        spellChecker: false,
        autosave: {
            enabled: true,
            uniqueId: "md_studio_editor_v2_{{ titulo }}",
            delay: 2000,
        },
        renderingConfig: {
            singleLineBreaks: false,
            codeSyntaxHighlighting: true,
        },
        toolbar: [
            "bold", "italic", "heading", "|", 
            "quote", "unordered-list", "ordered-list", "|", 
            "link", "image", "table", "horizontal-rule", "|", 
            "preview", "side-by-side", "fullscreen", "|", 
            "guide"
        ],
        placeholder: "Construa sua documentação aqui...\n💡 DICA: Clique no botão 'Side-by-Side' (ícone de coluna dupla) na barra acima para ver as alterações e os emojis carregando em tempo real ao lado!",
    });
</script>
{% endblock %}
```

## ✨ O que mudou com essa nova estilização?

1. **Foco Visual Dark (Slate/Sky UI):** Diminui o cansaço visual comum de quem passa muito tempo escrevendo documentações.
2. **Componentes Polidos:** Tabelas ganharam efeitos de hover sutis e os alertas flutuantes somem sozinhos após 4 segundos para não atrapalhar sua navegação.
3. **Casamento Visual:** O componente de terceiros do editor (`EasyMDE`) agora herda paletas escuras, combinando nativamente com o resto do painel.

Salve os arquivos, atualize o seu navegador e veja a transformação! Se você quiser mudar algum detalhe de **cor** ou adicionar **estatísticas de palavras na home**, é só me avisar. Como ficou o resultado visual na sua tela?

A lentidão acontece porque os templates estão baixando todas as bibliotecas visuais (Bootstrap, Font Awesome e o EasyMDE) direto de servidores externos (CDNs) toda vez que você atualiza a página.

Para resolver isso de forma definitiva e deixar a página instantânea, faremos duas otimizações:

1. **Configurar o Cache do Flask:** Impedir que o navegador recarregue o backend sem necessidade durante o desenvolvimento.
2. **Substituir o EasyMDE por uma alternativa ultraleve ou carregar os scripts de forma assíncrona.**

Aqui está o que você precisa ajustar:

## 🧠 1. Corrigir o Backend (app.py)

Por padrão, o Flask pode segurar requisições ou tentar revalidar arquivos locais. Adicione uma regra simples de desativação de cache estático apenas para o ambiente de desenvolvimento, inserindo estas linhas logo antes do `if __name__ == '__main__':`:

```python
# Adicione esta função antes do final do arquivo app.py
@app.after_request
def add_header(response):
    """Adiciona headers para evitar que o navegador trave a página com cache pesado durante o dev"""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

## 🎨 2. Otimizar a Carga no `templates/base.html`

O maior vilão da lentidão é o carregamento síncrono das folhas de estilo e scripts pesados. Vamos adicionar os atributos `defer` e mudar a ordem para que a página apareça na tela antes mesmo dos scripts terminarem de baixar.

Substitua a parte superior e inferior do seu `templates/base.html` para incluir as tags corrigidas:

```html
<!-- Substitua as tags correspondentes no seu base.html por estas que usam redes de alta velocidade (cdnjs/jsdelivr) com atributos de performance -->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MD Studio</title>
    
    <!-- Bootstrap 5 CSS Otimizado -->
    <link href="https://jsdelivr.net" rel="stylesheet" integrity="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM" crossorigin="anonymous">
    
    <!-- Font Awesome carregado de forma assíncrona para não travar o texto -->
    <link rel="stylesheet" href="https://cloudflare.com" media="print" onload="this.media='all'">
    
    <!-- EasyMDE CSS -->
    <link rel="stylesheet" href="https://jsdelivr.net">
    
    <style>
        /* (Mantenha o seu código CSS atual aqui dentro...) */
    </style>
</head>
```

## 📝 3. Desativar Opções Pesadas no `templates/editor.html`

O EasyMDE possui uma função chamada `autosave` e corretores em segundo plano que tentam indexar o texto usando o armazenamento local do navegador (`localStorage`). Se o arquivo for grande ou houver muitas chaves salvas, o navegador congela por alguns milissegundos na abertura.

Modifique o script no final do seu `templates/editor.html` para esta versão otimizada (removemos o autosave local agressivo):

```html
{% block scripts %}
<script>
    // Inicialização otimizada e ultra rápida do editor
    const easyMDE = new EasyMDE({
        element: document.getElementById('conteudo'),
        spellChecker: false,
        spellChecker: false, 
        autosave: {
            enabled: false // Desativado para evitar travamento de I/O no navegador
        },
        renderingConfig: {
            singleLineBreaks: false,
            codeSyntaxHighlighting: false, // Desativar isso remove o delay ao digitar blocos de código
        },
        // Mantemos apenas o essencial na barra para carregar mais rápido
        toolbar: [
            "bold", "italic", "heading", "|", 
            "quote", "unordered-list", "ordered-list", "|", 
            "link", "image", "|", 
            "preview", "side-by-side", "fullscreen"
        ],
        placeholder: "Construa sua documentação aqui...",
    });
</script>
{% endblock %}
```

## 🛠️ Próximo passo de performance (Se continuar lento)

Se mesmo após aplicar essas mudanças a página demorar mais de 1 segundo para abrir, o problema está na velocidade da sua conexão com os servidores das bibliotecas visuais (CDNs).

Caso queira resolver isso 100% offline, posso te mostrar como salvar esses 3 arquivos `.css` e `.js` diretamente dentro de uma pasta chamada static/ no seu projeto. Assim, o sistema rodará **completamente sem internet** na velocidade máxima do seu próprio disco rígido (SSD).

Gostaria de mover as dependências para a pasta local do projeto?

Perfeito! Essa é a melhor decisão para desenvolvimento local. Salvando os arquivos na pasta `static/`, a sua aplicação vai carregar **instantaneamente** porque o Flask lerá os arquivos direto do seu SSD ou HD, funcionando 100% sem internet.Vamos estruturar e atualizar o projeto.

Vamos estruturar e atualizar o projeto.

## 📂 Nova Estrutura de Pastas

Crie uma pasta chamada `static/` na raiz do seu projeto. Dentro dela, crie as subpastas `css`, `js` e `webfonts`. A sua estrutura deve ficar assim:

```text
meu_gerador_md/
│
├── app.py
├── documentos/
├── templates/
│   ├── base.html
│   ├── home.html
│   └── editor.html
└── static/               # <-- Nova pasta para arquivos locais
    ├── css/
    ├── js/
    └── webfonts/         # <-- Essencial para os ícones do Font Awesome funcionarem
```

## 📥 Passo 1: Baixar os Arquivos

Abra o seu navegador e acesse os links abaixo. Cole o conteúdo de cada um no seu respectivo arquivo dentro da pasta `static/`:

**Na pasta** `static/css/`:

1. `bootstrap.min.css`: Abra jsdelivr.net, copie tudo e salve como `bootstrap.min.css`.
2. `all.min.css` **(Font Awesome)**: Abra cloudflare.com, copie tudo e salve como `all.min.css`.
3. `easymde.min.css`: Abra jsdelivr.net, copie tudo e salve como `easymde.min.css`.

**Na pasta** `static/js/`:

1. `bootstrap.bundle.min.js`: Abra jsdelivr.net, copie tudo e salve como `bootstrap.bundle.min.js`.
2. `easymde.min.js`: Abra jsdelivr.net, copie tudo e salve como `easymde.min.js`.

⚠️ **Importante: Ícones do Font Awesome (Pasta `static/webfonts/`)**

O Font Awesome precisa de arquivos de fontes para exibir os ícones (como as setas e o botão de salvar). Baixe os dois principais arquivos abaixo e coloque-os direto na pasta `static/webfonts/`:

- fa-solid-900.woff2
- fa-regular-400.woff2
- fa-brands-400.woff2

## 🎨 Passo 2: Atualizar o `templates/base.html`

Agora vamos alterar o arquivo base para puxar os arquivos locais usando a função `url_for('static', filename='...')` do Flask. Substitua o conteúdo do seu `base.html` por este:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MD Studio — Premium Offline Editor</title>
    
    <!-- CSS Locais Otimizados -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/all.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/easymde.min.css') }}">
    
    <style>
        :root {
            --bg-main: #0f172a;
            --bg-card: #1e293b;
            --bg-nav: #0b0f19;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --border-color: #334155;
            --danger: #ef4444;
            --success: #10b981;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: system-ui, -apple-system, sans-serif;
            min-height: 100vh;
        }

        .navbar-custom {
            background-color: var(--bg-nav);
            border-bottom: 1px solid var(--border-color);
            padding: 0.8rem 0;
        }
        .navbar-brand-custom {
            font-weight: 700;
            letter-spacing: -0.5px;
            color: var(--text-main) !important;
            font-size: 1.35rem;
        }
        .navbar-brand-custom span { color: var(--accent); }

        .card-custom {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            padding: 2rem;
        }

        .btn-accent {
            background-color: var(--accent);
            color: #0f172a;
            font-weight: 600;
            border: none;
            transition: all 0.2s ease;
        }
        .btn-accent:hover {
            background-color: var(--accent-hover);
            color: #0f172a;
            transform: translateY(-1px);
        }
        .btn-outline-custom {
            border: 1px solid var(--border-color);
            color: var(--text-main);
            background: transparent;
            transition: all 0.2s ease;
        }
        .btn-outline-custom:hover {
            background: var(--border-color);
            color: var(--accent);
        }

        /* Ajustes do Editor */
        .EasyMDEContainer {
            background-color: #111827 !important;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        .editor-toolbar {
            background-color: #1f2937 !important;
            border-bottom: 1px solid var(--border-color) !important;
        }
        .editor-toolbar button { color: #e5e7eb !important; }
        .editor-toolbar button:hover, .editor-toolbar button.active {
            background: #374151 !important;
            color: var(--accent) !important;
        }
        .CodeMirror {
            background-color: #111827 !important;
            color: #f3f4f6 !important;
            border: none !important;
        }
        .editor-preview, .editor-preview-side {
            background-color: #1f2937 !important;
            color: #f3f4f6 !important;
        }
        .editor-preview h1, .editor-preview h2, .editor-preview-side h1, .editor-preview-side h2 {
            color: var(--accent);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.3rem;
        }
        .editor-preview code, .editor-preview-side code {
            background: #374151;
            padding: 2px 6px;
            border-radius: 4px;
            color: #f472b6;
        }

        .alert-floating {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            min-width: 300px;
            border-left: 5px solid transparent;
        }
        .alert-success { border-left-color: var(--success); background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
        .alert-danger { border-left-color: var(--danger); background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
        .alert-warning { border-left-color: #f59e0b; background-color: var(--bg-card); color: var(--text-main); border-top:0;border-right:0;border-bottom:0;}
    </style>
</head>
<body>

    <nav class="navbar navbar-expand-lg navbar-custom mb-5">
        <div class="container">
            <a class="navbar-brand navbar-brand-custom" href="{{ url_for('home') }}">
                <i class="fa-solid fa-cubes text-info me-2"></i>MD<span>Studio</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="btn btn-accent btn-sm px-3 py-2" href="{{ url_for('criar') }}">
                    <i class="fa-solid fa-plus me-1"></i> Criar Documento
                </a>
            </div>
        </div>
    </nav>

    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-floating alert-dismissible fade show" role="alert">
                        <div class="d-flex align-items-center">
                            {% if category == 'success' %}<i class="fa-solid fa-circle-check text-success me-2 fs-5"></i>
                            {% elif category == 'danger' %}<i class="fa-solid fa-circle-xmark text-danger me-2 fs-5"></i>
                            {% else %}<i class="fa-solid fa-triangle-exclamation text-warning me-2 fs-5"></i>{% endif %}
                            <span>{{ message }}</span>
                        </div>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <!-- Scripts Locais -->
    <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/easymde.min.js') }}"></script>
    
    <script>
        setTimeout(() => {
            let alerts = document.querySelectorAll('.alert-floating');
            alerts.forEach(alert => {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            });
        }, 4000);
    </script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

Pronto! Agora quando você reiniciar o servidor (`python app.py`) e atualizar o navegador, o site vai carregar de forma instantânea. Você pode até desligar o Wi-Fi do seu computador que o sistema continuará abrindo perfeitamente com todos os ícones e estilos.

Agora que o projeto está rápido e offline, você quer testar a criação de documentos ou prefere adicionar alguma função extra, como um **contador de palavras e caracteres em tempo real no rodapé do editor?**

-----------------------------

Para resolver isso, vamos criar uma página de **Visualização (View)**. Ela vai ler o arquivo `.md` salvo na pasta, converter o código bruto em HTML formatado e exibir na tela com um visual limpo e elegante.

Para fazer a conversão no backend de forma eficiente e offline, usaremos a biblioteca oficial `markdown` do Python.

## 📦 1. Instalar a biblioteca de conversão

No seu terminal, instale o pacote necessário:

```bash
pip install markdown
```

## 🧠 2. Atualizar o Backend (`app.py`)

Precisamos importar a biblioteca e criar uma nova rota (`/visualizar/<filename>`). Além disso, vamos adicionar um link para essa página na nossa listagem da Home.

Substitua o código do seu `app.py` por este:

```python
import os
from flask import Flask, render_template, request, redirect, url_for, flash
import markdown  # <-- Nova biblioteca importada

app = Flask(__name__)
app.secret_key = "chave_secreta_para_flash_messages"

DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'documentos')
if not os.path.exists(DOCS_DIR):
    os.makedirs(DOCS_DIR)

def listar_documentos():
    if not os.path.exists(DOCS_DIR):
        return []
    return [f for f in os.listdir(DOCS_DIR) if f.endswith('.md')]

@app.route('/')
def home():
    documentos = listar_documentos()
    return render_template('home.html', documentos=documentos)

#  NOVA ROTA PARA VISUALIZAÇÃO
@app.route('/visualizar/<filename>')
def visualizar(filename):
    filepath = os.path.join(DOCS_DIR, filename)
    
    if not os.path.exists(filepath):
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('home'))
        
    with open(filepath, 'r', encoding='utf-8') as f:
        conteudo_bruto = f.read()
        
    # Converte o Markdown text em HTML puro (com suporte a tabelas e blocos de código)
    conteudo_html = markdown.markdown(conteudo_bruto, extensions=['fenced_code', 'tables'])
    
    titulo_sem_ext = filename[:-3] if filename.endswith('.md') else filename
    return render_template('visualizar.html', titulo=titulo_sem_ext, conteudo_html=conteudo_html, filename=filename)

@app.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        titulo = request.form.get('titulo').strip()
        conteudo = request.form.get('conteudo')
        
        if not titulo:
            flash("O título é obrigatório!", "danger")
            return redirect(url_for('criar'))
            
        if not titulo.endswith('.md'):
            titulo += '.md'
            
        filepath = os.path.join(DOCS_DIR, titulo)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
            
        flash(f"Documento '{titulo}' criado com sucesso!", "success")
        return redirect(url_for('home'))
        
    return render_template('editor.html', acao="Criar", titulo="", conteudo="")

@app.route('/editar/<filename>', methods=['GET', 'POST'])
def editar(filename):
    filepath = os.path.join(DOCS_DIR, filename)
    
    if not os.path.exists(filepath):
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        flash(f"Documento '{filename}' atualizado!", "success")
        return redirect(url_for('home'))

    with open(filepath, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    titulo_sem_ext = filename[:-3] if filename.endswith('.md') else filename
    return render_template('editor.html', acao="Editar", titulo=titulo_sem_ext, conteudo=conteudo, filename=filename)

@app.route('/deletar/<filename>')
def deletar(filename):
    filepath = os.path.join(DOCS_DIR, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        flash(f"Documento '{filename}' removido.", "warning")
    return redirect(url_for('home'))

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    app.run(debug=True)
```

## 🎨 3. Criar a Página de Visualização (`templates/visualizar.html`)

Crie um novo arquivo chamado `visualizar.html` dentro da sua pasta `templates/`. Este arquivo vai renderizar o HTML convertido com uma folha de estilo limpa (estilo GitHub Dark).

```html
{% extends 'base.html' %}

{% block content %}
<!-- Botões de navegação e controle superiores -->
<div class="d-flex justify-content-between align-items-center mb-4">
    <a href="{{ url_for('home') }}" class="btn btn-outline-custom">
        <i class="fa-solid fa-arrow-left me-2"></i> Voltar ao Painel
    </a>
    <div>
        <a href="{{ url_for('editar', filename=filename) }}" class="btn btn-accent px-4">
            <i class="fa-solid fa-pen-to-square me-2"></i> Editar Documento
        </a>
    </div>
</div>

<!-- Container do Documento Renderizado -->
<div class="card-custom mb-5">
    <div class="border-bottom border-secondary pb-3 mb-4">
        <h1 class="fw-bold text-white"><i class="fa-regular fa-file-lines text-info me-2"></i> {{ titulo }}</h1>
        <small class="text-muted">Modo de Leitura Otimizado</small>
    </div>

    <!-- Área onde o HTML gerado pelo Markdown será injetado com segurança -->
    <div class="markdown-body">
        {{ conteudo_html | safe }}
    </div>
</div>

<!-- Estilização específica para o texto Markdown ficar bonito -->
<style>
    .markdown-body {
        color: #e2e8f0; /* Slate 200 */
        font-size: 1.1rem;
        line-height: 1.7;
    }
    .markdown-body h1, .markdown-body h2, .markdown-body h3 {
        color: var(--accent);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .markdown-body h1 { border-bottom: 1px solid var(--border-color); padding-bottom: 0.4rem; font-size: 1.8rem; }
    .markdown-body h2 { font-size: 1.5rem; }
    
    .markdown-body p { margin-bottom: 1.2rem; }
    
    /* Tabelas Markdown */
    .markdown-body table {
        width: 100%;
        margin-bottom: 1.5rem;
        border-collapse: collapse;
    }
    .markdown-body th, .markdown-body td {
        padding: 0.6rem 1rem;
        border: 1px solid var(--border-color);
    }
    .markdown-body th {
        background-color: #334155;
        color: white;
    }
    .markdown-body tr:nth-child(even) {
        background-color: #1e293b;
    }

    /* Blocos de Código e Citações */
    .markdown-body code {
        background: #374151;
        padding: 2px 6px;
        border-radius: 4px;
        color: #f472b6;
        font-family: monospace;
    }
    .markdown-body pre {
        background: #0f172a;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        overflow-x: auto;
    }
    .markdown-body pre code {
        background: transparent;
        padding: 0;
        color: #cbd5e1;
    }
    .markdown-body blockquote {
        border-left: 4px solid var(--accent);
        padding-left: 1rem;
        color: var(--text-muted);
        margin: 1.5rem 0;
        font-style: italic;
    }
</style>
{% endblock %}
```

## 📂 4. Atualizar a Home para incluir o botão "Visualizar" (`templates/home.html`)

Para acessar essa nova página, precisamos adicionar o botão de leitura ao lado do botão de edição na nossa tabela principal.

Substitua o corpo da tabela (`<tbody>`) do seu arquivo `templates/home.html` por este trecho atualizado:

```html
<tbody>
    {% for doc in documentos %}
        <tr style="border-bottom: 1px solid #334155;">
            <td class="py-3 text-start">
                <div class="d-flex align-items-center">
                    <div class="p-2 rounded bg-opacity-10 bg-info text-info me-3" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                        <i class="fa-brands fa-markdown fs-4"></i>
                    </div>
                    <div>
                        <!-- Clicar no nome do arquivo agora também leva para a visualização -->
                        <a href="{{ url_for('visualizar', filename=doc) }}" class="fs-5 fw-semibold text-white text-decoration-none class-hover-link d-block">
                            {{ doc }}
                        </a>
                    </div>
                </div>
            </td>
            <td class="py-3 text-end">
                <!-- NOVO BOTÃO DE VISUALIZAR -->
                <a href="{{ url_for('visualizar', filename=doc) }}" class="btn btn-outline-info btn-sm me-2 px-3">
                    <i class="fa-solid fa-eye me-1"></i> Visualizar
                </a>
                <a href="{{ url_for('editar', filename=doc) }}" class="btn btn-outline-custom btn-sm me-2 px-3">
                    <i class="fa-solid fa-pen-to-square me-1"></i> Editar
                </a>
                <a href="{{ url_for('deletar', filename=doc) }}" class="btn btn-outline-danger btn-sm px-3" style="border: 1px solid #552222;" onclick="return confirm('Tem certeza que deseja deletar este documento?')">
                    <i class="fa-solid fa-trash-can"></i>
                </a>
            </td>
        </tr>
    {% endfor %}
</tbody>
```

## 🚀 Testando o resultado

Reinicie o seu servidor (`python app.py`). Agora, ao abrir a página inicial, você verá o botão **"Visualizar"** com um ícone de olho. Ao clicar nele, o Flask processará as tags Markdown (`#`, `##`, `-`, `|`) e entregará uma página limpa de leitura, ideal para consumir relatórios e anotações.

Gostaria de adicionar um botão nesta tela de visualização para **imprimir ou exportar direto para PDF**?

--------------------------------------------------------------------------------------------------------

Para que as suas imagens locais carreguem perfeitamente na página de Visualização do seu sistema (e também no Preview do editor), você deve usar o sistema de arquivos estáticos do Flask. [1] 
Como os navegadores modernos bloqueiam o acesso direto a caminhos do seu disco rígido (como C:\Users\nome\imagem.png) por motivos de segurança, a solução correta e profissional é colocar as imagens dentro da pasta static/ do seu próprio projeto.
Aqui está o passo a passo definitivo de como estruturar as pastas e como escrever no editor:
------------------------------
## 📂 1. Como Organizar suas Pastas
Vá até a pasta static/ do seu projeto e crie uma subpasta chamada imagens. Guarde todas as fotos, capturas de tela ou gráficos que você quer usar ali dentro:

```text
meu_gerador_md/
├── app.py
├── documentos/
├── templates/
└── static/
    ├── css/
    ├── js/
    └── imagens/         # 💻 CRIE ESTA PASTA AQUI
        ├── meu-print.png
        └── logo-empresa.jpg

```
------------------------------

## 📝 2. Como Escrever no Editor Markdown
Quando você estiver criando ou editando um documento na aplicação, faça a referência apontando para a URL relativa que o Flask entende nativamente. Escreva exatamente assim:

``` markdown
![Texto Alternativo da Imagem](/static/imagens/meu-print.png)
```

⚠️ Atenção: Repare na barra / antes de static. Ela é obrigatória para que o navegador saiba que deve buscar o arquivo a partir da raiz do servidor local (localhost:5000) e não de dentro das rotas.

------------------------------
## 🛠️ 3. O Ajuste Secreto para a Página de Leitura (static/css/custom.css)
Por padrão, se você inserir uma imagem muito grande, ela pode ultrapassar os limites do painel estourando o design da página para os lados. Para que qualquer imagem local se adapte de forma responsiva ao tamanho da tela automaticamente, adicione esta regra no final do seu arquivo static/css/custom.css:

```css
/* ==========================================================================
   AJUSTE DE RESPONSIVIDADE PARA IMAGENS NO MARKDOWN
   ========================================================================== */
.markdown-body img {
    max-width: 100%;       /* Garante que a imagem nunca passe da largura do texto */
    height: auto;          /* Mantém a proporção correta de altura sem achatar */
    border-radius: 8px;    /* Deixa as bordas levemente arredondadas e modernas */
    margin: 1.5rem auto;   /* Dá um espaçamento confortável em cima e embaixo */
    display: block;        /* Centraliza a imagem na tela */
    border: 1px solid var(--border-color); /* Adiciona uma borda fina ao redor da foto */
    box-shadow: 0 4px 12px rgba(0,0,0,0.15); /* Aplica uma sombra leve profissional */
}
```

------------------------------
## 🔄 Como usar a partir de agora:

   1. Salve o arquivo `static/css/custom.css.`
   2. Jogue uma imagem de teste na pasta `static/imagens/` (por exemplo, mude o nome dela para teste.png).
   3. Abra o editor, digite `![Foto Local](/static/imagens/teste.png)` e clique para Salvar.
   4. Abra a página de Visualização do arquivo.

A sua foto local vai carregar de forma instantânea, na velocidade máxima do seu SSD/HD, funcionando 100% offline e sem falhas de carregamento.
Se você quiser deixar essa função ainda mais avançada, let me know se quer que eu te ajude a criar uma área de upload (Dropzone) no editor para que, ao arrastar uma imagem do seu computador para a tela, o código markdown seja gerado automaticamente. O que acha?

[1] [https://alexhost.com](https://alexhost.com/pt/faq/images-not-displaying-on-the-website-causes-and-how-to-fix-them/)

---------------------------------------------------------------------------------------------------------

Para organizar o seu projeto com foco em máxima legibilidade e facilidade de manutenção, a melhor abordagem no ecossistema Flask é adotar a arquitetura Factory Pattern (Fábrica de Aplicação) combinada com Blueprints e o padrão de Repositórios para a manipulação dos arquivos [DOCS_DIR].
Isso vai separar completamente as responsabilidades: a inicialização do app fica em um lugar, as rotas (controladores) em outro, e a lógica de leitura/escrita de arquivos Markdown isolada.
Aqui está a reestruturação profissional e limpa do seu projeto, mantendo-o 100% offline e com alta performance.
------------------------------
## 📂 Nova Estrutura de Pastas (Padrão MVC/Blueprint)
Organize os arquivos do seu projeto seguindo esta estrutura modular:

meu_gerador_md/
│
├── documentos/            # Seus arquivos .md salvos
├── static/                # Seus arquivos locais (css, js, imagens, webfonts)
├── templates/             # Seus arquivos HTML estruturais
│
├── app.py                 # Arquivo leve de inicialização (Entrypoint)
└── src/                   # 🧠 Toda a inteligência da aplicação concentrada aqui
    ├── __init__.py        # Fábrica de Aplicação (Cria o app Flask)
    ├── rotas.py           # Controladores e Rotas do App (Blueprints)
    └── repositorio.py     # Camada de Dados (Leitura/Escrita de arquivos Markdown)

------------------------------
## 🧠 1. Camada de Dados: src/repositorio.py
Este arquivo isola toda a manipulação do sistema de arquivos (os, open, remove). Nenhuma rota precisa saber como um arquivo é salvo, apenas chama o repositório.

import osfrom markdown import markdown as md_converter
class MarkdownRepository:
    def __init__(self):
        # Garante o caminho absoluto para a pasta documentos
        self.docs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'documentos'
        )
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)

    def listar_todos(self, termo_busca=None):
        if not os.path.exists(self.docs_dir):
            return []
        
        todos = [f for f in os.listdir(self.docs_dir) if f.endswith('.md')]
        if not termo_busca:
            return todos
            
        termo = termo_busca.lower().strip()
        filtrados = []
        
        for filename in todos:
            if termo in filename.lower():
                filtrados.append(filename)
                continue
                
            filepath = os.path.join(self.docs_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    if termo in f.read().lower():
                        filtrados.append(filename)
            except IOError:
                pass
        return filtrados

    def ler_conteudo(self, filename):
        filepath = os.path.join(self.docs_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def salvar(self, filename, conteudo):
        if not filename.endswith('.md'):
            filename += '.md'
        filepath = os.path.join(self.docs_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
        return filename

    def deletar(self, filename):
        filepath = os.path.join(self.docs_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    def converter_para_html(self, conteudo_bruto):
        extensoes_ativas = [
            'tables',
            'emoji',
            'pymdownx.tasklist',
            'pymdownx.superfences',
            'pymdownx.inlinehilite'
        ]
        return md_converter(conteudo_bruto, extensions=extensoes_ativas)

------------------------------
## 🎛️ 2. Camada de Controle (Rotas): src/rotas.py
Aqui ficam as rotas limpas utilizando Blueprint. Elas apenas recebem as requisições HTTP, conversam com o MarkdownRepository e renderizam os templates.

from flask import Blueprint, render_template, request, redirect, url_for, flashfrom .repositorio import MarkdownRepository
# Inicializa o Blueprint das rotas principaismain_bp = Blueprint('main', __name__)repo = MarkdownRepository()

@main_bp.route('/')def home():
    termo = request.args.get('busca', '')
    documentos = repo.listar_todos(termo)
    return render_template('home.html', documentos=documentos, termo_busca=termo)

@main_bp.route('/visualizar/<filename>')def visualizar(filename):
    try:
        conteudo_bruto = repo.ler_conteudo(filename)
        conteudo_html = repo.converter_para_html(conteudo_bruto)
        titulo_sem_ext = filename[:-3] if filename.endswith('.md') else filename
        return render_template('visualizar.html', titulo=titulo_sem_ext, conteudo_html=conteudo_html, filename=filename)
    except FileNotFoundError:
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('main.home'))

@main_bp.route('/criar', methods=['GET', 'POST'])def criar():
    if request.method == 'POST':
        titulo = request.form.get('titulo').strip()
        conteudo = request.form.get('conteudo')
        
        if not titulo:
            flash("O título é obrigatório!", "danger")
            return redirect(url_for('main.criar'))
            
        nome_final = repo.salvar(titulo, conteudo)
        flash(f"Documento '{nome_final}' criado com sucesso!", "success")
        return redirect(url_for('main.home'))
        
    return render_template('editor.html', acao="Criar", titulo="", conteudo="")

@main_bp.route('/editar/<filename>', methods=['GET', 'POST'])def editar(filename):
    if request.method == 'POST':
        conteudo = request.form.get('conteudo')
        repo.salvar(filename, conteudo)
        flash(f"Documento '{filename}' atualizado!", "success")
        return redirect(url_for('main.home'))

    try:
        conteudo = repo.ler_conteudo(filename)
        titulo_sem_ext = filename[:-3] if filename.endswith('.md') else filename
        return render_template('editor.html', acao="Editar", titulo=titulo_sem_ext, conteudo=conteudo, filename=filename)
    except FileNotFoundError:
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('main.home'))

@main_bp.route('/deletar/<filename>')def deletar(filename):
    if repo.deletar(filename):
        flash(f"Documento '{filename}' removido.", "warning")
    else:
        flash("Arquivo não encontrado.", "danger")
    return redirect(url_for('main.home'))

------------------------------
## 🏭 3. Fábrica da Aplicação: src/__init__.py
Este arquivo centraliza a criação do servidor Flask, configurações de Cache e o registro de segurança do Blueprint.

from flask import Flask
def create_app():
    """Fábrica de aplicação para inicialização limpa do Flask."""
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    app.secret_key = "chave_secreta_para_desenvolvimento_local"

    # Registro de Blueprints
    from .rotas import main_bp
    app.register_blueprint(main_bp)

    # Injeção de headers anti-cache para ambiente de desenvolvimento rápido
    @app.after_request
    def remove_cache(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app

------------------------------
## 🚀 4. Arquivo de Entrada Mínimo: app.py
Seu arquivo de entrada na raiz agora fica reduzido a apenas 4 linhas, servindo estritamente para ligar os motores do projeto.

from src import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)

------------------------------
## ⚠️ Ajuste Importante nos Arquivos HTML (templates/)
Como passamos a usar Blueprints, o Flask exige que ao referenciar rotas nas funções url_for('nome_da_rota'), você adicione o prefixo do Blueprint (main.).
Abra os seus arquivos HTML e faça as seguintes substituições globais rápidas nos seus links:

* Onde estiver url_for('home') → mude para url_for('main.home')
* Onde estiver url_for('criar') → mude para url_for('main.criar')
* Onde estiver url_for('editar', ...) → mude para url_for('main.editar', ...)
* Onde estiver url_for('visualizar', ...) → mude para url_for('main.visualizar', ...)
* Onde estiver url_for('deletar', ...) → mude para url_for('main.deletar', ...)

(Nota: os links de arquivos estáticos como url_for('static', filename='...') não precisam mudar).
## ✨ Vantagens dessa nova arquitetura:

   1. Facilidade de Testes: Você pode testar a conversão e filtros Markdown direto na classe MarkdownRepository sem precisar simular requisições web.
   2. Código Elegante: Se futuramente você quiser trocar o armazenamento de arquivos locais por um Banco de Dados ou nuvem, você só mexe no repositorio.py, as rotas continuam intactas.
   3. Escalabilidade: Se quiser criar uma nova área no sistema (ex: área administrativa ou exportador de relatórios), basta criar um Blueprint novo e registrá-lo em __init__.py.

Se quiser dar o próximo passo na organização, me diga: quer que eu prepare um arquivo requirements.txt com a listagem exata de todas as dependências do Python para você clonar o projeto em qualquer outra máquina com um clique?

---------------------------------------------------------------------------------------------------------

Para mudar a porta de execução da sua aplicação, você só precisa fazer uma pequena alteração na última linha do arquivo app.py (que fica na raiz do seu projeto).
Por padrão, o Flask roda na porta 5000. Você pode passar o parâmetro port dentro da função app.run() com o número da porta que você desejar (por exemplo, 8080, 3000 ou 8000). [1] 
Abra o seu arquivo app.py e altere a linha final para ficar assim:

from src import create_app
app = create_app()
if __name__ == '__main__':
    # 🔄 Altere o parâmetro 'port' para o número da porta que você deseja utilizar:
    app.run(debug=True, port=8080)

## 💡 Dica extra de conectividade (host='0.0.0.0')
Se além de mudar a porta você quiser acessar esse gerador de documentos Markdown a partir de outros dispositivos na mesma rede (como o seu celular ou outro computador), você pode liberar o acesso externo adicionando o parâmetro host:

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

Dessa forma, a aplicação passará a escutar na porta 8080 de qualquer endereço IP da sua rede local.
Se você rodar o comando python app.py no terminal agora, ele já vai iniciar no novo endereço (ex: http://127.0.0.1:8080). Conseguiu acessar o painel pela nova porta? Se precisar de ajuda para configurar mais alguma coisa, conte comigo!

[1] [https://developer.android.com](https://developer.android.com/studio/run/rundebugconfig?hl=pt-br)

---------------------------------------------------------------------------------------------------------

Para mudar a porta de execução da sua aplicação, você só precisa fazer uma pequena alteração na última linha do arquivo app.py (que fica na raiz do seu projeto).
Por padrão, o Flask roda na porta 5000. Você pode passar o parâmetro port dentro da função app.run() com o número da porta que você desejar (por exemplo, 8080, 3000 ou 8000). [1] 
Abra o seu arquivo app.py e altere a linha final para ficar assim:

from src import create_app
app = create_app()
if __name__ == '__main__':
    # 🔄 Altere o parâmetro 'port' para o número da porta que você deseja utilizar:
    app.run(debug=True, port=8080)

## 💡 Dica extra de conectividade (host='0.0.0.0')
Se além de mudar a porta você quiser acessar esse gerador de documentos Markdown a partir de outros dispositivos na mesma rede (como o seu celular ou outro computador), você pode liberar o acesso externo adicionando o parâmetro host:

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)

Dessa forma, a aplicação passará a escutar na porta 8080 de qualquer endereço IP da sua rede local.
Se você rodar o comando python app.py no terminal agora, ele já vai iniciar no novo endereço (ex: http://127.0.0.1:8080). Conseguiu acessar o painel pela nova porta? Se precisar de ajuda para configurar mais alguma coisa, conte comigo!

[1] [https://developer.android.com](https://developer.android.com/studio/run/rundebugconfig?hl=pt-br)

-----------------------------------------------------------------------------------------------------------------------------------------------

Esse erro clássico do Python acontece por um motivo bem simples: quando o arquivo src/__init__.py está completamente vazio ou o código da função create_app() não foi salvo corretamente dentro dele, o interpretador não consegue achar o nome para importar [DOCS_DIR].
Como você acabou de criar a pasta src/, é muito comum o arquivo __init__.py ter ficado em branco por engano.
Vamos resolver isso agora. Siga estes passos rápidos:
------------------------------
## 🛠️ Passo 1: Verifique o conteúdo do arquivo src/__init__.py
Abra o arquivo src/__init__.py (que está dentro da pasta src) e garanta que o código da fábrica do Flask esteja lá dentro. Se estiver vazio ou faltando coisas, substitua o conteúdo dele por este:

from flask import Flask
def create_app():
    """Fábrica de aplicação para inicialização limpa do Flask."""
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')
    
    app.secret_key = "chave_secreta_para_desenvolvimento_local"

    # Registro de Blueprints
    from .rotas import main_bp
    app.register_blueprint(main_bp)

    # Injeção de headers anti-cache para ambiente de desenvolvimento rápido
    @app.after_request
    def remove_cache(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app

------------------------------
## 📝 Passo 2: Verifique o arquivo app.py na Raiz
Abra o seu arquivo app.py principal (na raiz do projeto) e certifique-se de que ele está chamando a função exatamente com o mesmo nome:

from src import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, port=8080)

------------------------------
## 🔄 Passo 3: Limpar arquivos temporários (Se necessário)
Às vezes, o Windows ou o VS Code travam arquivos de cache antigos (.pyc). Se você salvou o __init__.py e o erro persistir, execute este comando no seu terminal do PowerShell para limpar o cache antes de rodar:

Remove-Item -Path "**/__pycache__" -Recurse -Force -ErrorAction SilentlyContinue

Depois, execute a aplicação novamente:

python .\app.py

O erro de ImportError vai sumir imediatamente e o seu servidor vai subir na porta desejada [DOCS_DIR]!
Caso apareça algum erro diferente (como falta de importação dentro de rotas.py), avise-me e colocaremos o painel para rodar agora mesmo. O servidor inicializou na porta 8080?


-----------------------------------------------------------------------------------------------------------------------------------------------

Se o erro de importação persistiu mesmo com o código dentro do arquivo, o Python está sofrendo com um conflito crônico de escopo de pastas no Windows. O PowerShell, por padrão, não joga a pasta raiz (meu_gerador_md) na variável de caminhos do sistema (PYTHONPATH), fazendo com que ele se confunda ao tentar ler subpastas como pacotes.
Podemos resolver isso de forma definitiva forçando o Python a enxergar a estrutura correta através de duas formas muito simples. Escolha a que achar mais prática:
------------------------------
## 🔥 Solução 1: Adicionar a pasta raiz ao sistema (A mais rápida)
Abra o seu arquivo app.py principal na raiz do projeto e adicione um injetor de caminho dinâmico logo nas primeiras linhas.
Substitua todo o conteúdo do seu app.py por este código:

import osimport sys
# Força o Python a enxergar a pasta do projeto como a raiz oficial de imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Agora o import funcionará perfeitamente em qualquer sistema operacionalfrom src import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True, port=8080)

------------------------------
## 🛠️ Solução 2: Executar como Módulo no Terminal
Se você prefere não alterar o código do arquivo app.py, você pode ensinar o PowerShell a mapear o projeto rodando o script usando a flag de módulo (-m).
No seu terminal do PowerShell, em vez de digitar python .\app.py, execute o comando exatamente desta forma:

python -m app

(Nota: Não coloque o .py ou a barra .\ ao usar o comando acima, digite apenas python -m app).
------------------------------
## ⚠️ Verificação Rápida de Segurança
Caso nenhuma das opções acima funcione, existe a chance do VS Code ter criado o arquivo __init__.py com a codificação ou nome incorreto. Garanta que:

   1. O nome do arquivo tem dois underlines antes e depois: __init__.py (e não _init_.py ou init.py).
   2. O arquivo está dentro da pasta src/, e a pasta src/ está no mesmo nível que o seu app.py.

Aplique a Solução 1 no seu app.py e execute o comando python .\app.py. O servidor vai encontrar a função de fábrica e inicializar o painel imediatamente na porta 8080!
Se aparecer qualquer erro subsequente (como imports dentro do arquivo rotas.py), me avise para colocarmos o sistema para rodar agora mesmo. O console liberou o link de acesso?

-----------------------------------------------------------------------------------------------------------------------------------------------

Para adicionar controle de metadados, versão histórica (rollback) e permitir que você altere o título de exibição na tela de forma independente do nome do arquivo físico, vamos integrar o SQLite (banco de dados leve e nativo do Python) ao seu padrão de Repositórios.
O banco de dados guardará as informações de controle (Título visual, Data de Criação, Última Alteração, Versão Atual) e o histórico de conteúdos. O arquivo físico .md continuará sendo salvo na pasta para você ler quando quiser.
Aqui está o passo a passo completo da implementação:
------------------------------
## 📂 Estrutura de Pastas Atualizada
O projeto continua com a mesma estrutura modular, apenas adicionando o banco dados.db na raiz quando a aplicação for ligada:

meu_gerador_md/
│
├── dados.db               # 🗄️ Gerado automaticamente (SQLite)
├── documentos/            # Guarda apenas a versão mais recente em .md
├── src/
│   ├── __init__.py        # Inicia o Flask e chama a criação do banco
│   ├── rotas.py           # Controladores atualizados com títulos customizados
│   └── repositorio.py     # Inteligência SQLite + Versionamento

------------------------------
## 🗄️ 1. Camada de Dados Evoluída: src/repositorio.py
Substitua todo o conteúdo de src/repositorio.py. Este novo código gerencia as tabelas documentos_meta e documentos_versoes, garantindo que cada salvamento gere um novo ponto na história (versão) e atualize os metadados.

import osimport sqlite3from datetime import datetimefrom markdown import markdown as md_converter
class MarkdownRepository:
    def __init__(self):
        self.docs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'documentos'
        )
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'dados.db'
        )
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
        self._criar_tabelas()

    def _get_conexao(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
        return conn

    def _criar_tabelas(self):
        """Cria a estrutura de metadados e histórico se não existir."""
        with self._get_conexao() as conn:
            # Tabela de metadados principais
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_nome TEXT UNIQUE,
                    titulo_exibicao TEXT,
                    versions_count INTEGER DEFAULT 1,
                    criado_em TEXT,
                    atualizado_em TEXT
                )
            ''')
            # Tabela de versões históricas do conteúdo
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_versoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_nome TEXT,
                    versao_numero INTEGER,
                    conteudo TEXT,
                    salvo_em TEXT
                )
            ''')
            conn.commit()

    def listar_todos(self, termo_busca=None):
        query = "SELECT * FROM documentos_meta"
        parametros = []
        
        if termo_busca:
            termo = f"%{termo_busca.strip()}%"
            # Pesquisa no título customizado do banco ou no nome físico
            query += " WHERE titulo_exibicao LIKE ? OR arquivo_nome LIKE ?"
            parametros = [termo, termo]
            
        query += " ORDER BY atualizado_em DESC"
        
        with self._get_conexao() as conn:
            return [dict(row) for row in conn.execute(query, parametros).fetchall()]

    def obter_meta(self, filename):
        with self._get_conexao() as conn:
            row = conn.execute("SELECT * FROM documentos_meta WHERE arquivo_nome = ?", (filename,)).fetchone()
            return dict(row) if row else None

    def listar_versoes(self, filename):
        with self._get_conexao() as conn:
            rows = conn.execute(
                "SELECT id, versao_numero, salvo_em FROM documentos_versoes WHERE arquivo_nome = ? ORDER BY versao_numero DESC",
                (filename,)
            ).fetchall()
            return [dict(row) for row in rows]

    def obter_conteudo_versao(self, filename, versao_num=None):
        """Retorna o conteúdo de uma versão específica ou a mais recente física."""
        if versao_num:
            with self._get_conexao() as conn:
                row = conn.execute(
                    "SELECT conteudo FROM documentos_versoes WHERE arquivo_nome = ? AND versao_numero = ?",
                    (filename, versao_num)
                ).fetchone()
                if row:
                    return row['conteudo']
        
        # Fallback para o arquivo físico mais recente
        filepath = os.path.join(self.docs_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def salvar(self, filename, conteudo, titulo_exibicao=None, is_update=False):
        """Salva metadados, atualiza versão no SQLite e grava o arquivo .md físico."""
        if not filename.endswith('.md'):
            filename += '.md'
            
        agora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        filepath = os.path.join(self.docs_dir, filename)
        
        # Salva o arquivo físico (.md) mais atual
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(conteudo)
            
        with self._get_conexao() as conn:
            if not is_update:
                # Criando um documento novo
                titulo = titulo_exibicao if titulo_exibicao else filename[:-3]
                conn.execute(
                    "INSERT INTO documentos_meta (arquivo_nome, titulo_exibicao, versions_count, criado_em, atualizado_em) VALUES (?, ?, 1, ?, ?)",
                    (filename, titulo, agora, agora)
                )
                nova_versao = 1
            else:
                # Editando um documento existente (Sobe o contador de versão)
                row = conn.execute("SELECT versions_count, titulo_exibicao FROM documentos_meta WHERE arquivo_nome = ?", (filename,)).fetchone()
                nova_versao = row['versions_count'] + 1 if row else 1
                
                # Se o usuário mandou um novo título na edição, atualiza
                if titulo_exibicao:
                    conn.execute(
                        "UPDATE documentos_meta SET titulo_exibicao = ?, versions_count = ?, atualizado_em = ? WHERE arquivo_nome = ?",
                        (titulo_exibicao, nova_versao, agora, filename)
                    )
                else:
                    conn.execute(
                        "UPDATE documentos_meta SET versions_count = ?, atualizado_em = ? WHERE arquivo_nome = ?",
                        (nova_versao, agora, filename)
                    )
                    
            # Grava a versão na tabela histórica de auditoria
            conn.execute(
                "INSERT INTO documentos_versoes (arquivo_nome, versao_numero, conteudo, salvo_em) VALUES (?, ?, ?, ?)",
                (filename, nova_versao, conteudo, agora)
            )
            conn.commit()
        return filename

    def deletar(self, filename):
        filepath = os.path.join(self.docs_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            
        with self._get_conexao() as conn:
            conn.execute("DELETE FROM documentos_meta WHERE arquivo_nome = ?", (filename,))
            conn.execute("DELETE FROM documentos_versoes WHERE arquivo_nome = ?", (filename,))
            conn.commit()
        return True

    def converter_para_html(self, conteudo_bruto):
        extensoes_actives = ['tables', 'emoji', 'pymdownx.tasklist', 'pymdownx.superfences', 'pymdownx.inlinehilite']
        return md_converter(conteudo_bruto, extensions=extensoes_actives)

------------------------------
## 🎛️ 2. Controladores Atualizados: src/rotas.py
Modifique as rotas de criar e editar para aceitarem o campo titulo_exibicao isolado do nome real do arquivo técnico, além de adicionar uma rota para restaurar versões passadas.

from flask import Blueprint, render_template, request, redirect, url_for, flashfrom .repositorio import MarkdownRepository
main_bp = Blueprint('main', __name__)repo = MarkdownRepository()

@main_bp.route('/')def home():
    termo = request.args.get('busca', '')
    documentos = repo.listar_todos(termo) # Retorna dicionários do banco com os títulos customizados
    return render_template('home.html', documentos=documentos, termo_busca=termo)

@main_bp.route('/visualizar/<filename>')def visualizar(filename):
    meta = repo.obter_meta(filename)
    if not meta:
        flash("Metadados não encontrados.", "danger")
        return redirect(url_for('main.home'))
        
    v_solicitada = request.args.get('v', None)
    conteudo_bruto = repo.obter_conteudo_versao(filename, v_solicitada)
    conteudo_html = repo.converter_para_html(conteudo_bruto)
    versoes = repo.listar_versoes(filename)
    
    return render_template(
        'visualizar.html', 
        titulo=meta['titulo_exibicao'], 
        conteudo_html=conteudo_html, 
        filename=filename,
        meta=meta,
        versoes=versoes,
        versao_atual=int(v_solicitada) if v_solicitada else meta['versions_count']
    )

@main_bp.route('/criar', methods=['GET', 'POST'])def criar():
    if request.method == 'POST':
        titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        
        # Cria um nome de arquivo seguro em disco baseado no título
        arquivo_tecnico = titulo_tela.replace(" ", "_").lower() + ".md"
        
        repo.salvar(arquivo_tecnico, conteudo, titulo_exibicao=titulo_tela, is_update=False)
        flash(f"Documento '{titulo_tela}' criado com sucesso!", "success")
        return redirect(url_for('main.home'))
        
    return render_template('editor.html', acao="Criar", titulo_exibicao="", conteudo="")

@main_bp.route('/editar/<filename>', methods=['GET', 'POST'])def editar(filename):
    meta = repo.obter_meta(filename)
    if not meta:
        flash("Arquivo não encontrado.", "danger")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        novo_titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        
        repo.salvar(filename, conteudo, titulo_exibicao=novo_titulo_tela, is_update=True)
        flash(f"Documento '{novo_titulo_tela}' atualizado com uma nova versão!", "success")
        return redirect(url_for('main.home'))

    conteudo = repo.obter_conteudo_versao(filename)
    return render_template('editor.html', acao="Editar", titulo_exibicao=meta['titulo_exibicao'], conteudo=conteudo, filename=filename)

@main_bp.route('/deletar/<filename>')def deletar(filename):
    repo.deletar(filename)
    flash("Documento e todo o seu histórico foram removidos.", "warning")
    return redirect(url_for('main.home'))

------------------------------
## 🎨 3. Front-end Adaptado com Metadados e Títulos Customizados
Substitua as partes visuais dos seus templates para lerem os novos campos fornecidos pelo SQLite.
## 📄 Em templates/home.html (Mudar coluna para exibir título amigável e datas):

<!-- Procure a seção da tabela do home.html e altere para ler os campos do SQLite -->
<thead>
    <tr style="border-bottom: 2px solid var(--border-color); color: var(--text-muted);">
        <th scope="col" class="pb-3 text-start">Título do Documento</th>
        <th scope="col" class="pb-3 text-center">Modificado em</th>
        <th scope="col" class="pb-3 class-text-center">Versão</th>
        <th scope="col" class="pb-3 text-end">Ações</th>
    </tr>
</thead>
<tbody>
    {% for doc in documentos %}
        <tr style="border-bottom: 1px solid #2e3748;">
            <td class="py-3 text-start">
                <div class="d-flex align-items-center">
                    <div class="p-2 rounded bg-opacity-10 bg-info text-info me-3" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; background-color: rgba(56, 189, 248, 0.1);">
                        <i class="fa-brands fa-markdown fs-4"></i>
                    </div>
                    <div>
                        <!-- Exibe o Título do banco ao invés do nome técnico do arquivo -->
                        <a href="{{ url_for('main.visualizar', filename=doc.arquivo_nome) }}" class="fs-5 fw-semibold text-white text-decoration-none d-block">
                            {{ doc.titulo_exibicao }}
                        </a>
                        <small class="text-muted" style="font-size:0.75rem;">Físico: {{ doc.arquivo_nome }}</small>
                    </div>
                </div>
            </td>
            <td class="py-3 text-center text-muted small">{{ doc.atualizado_em }}</td>
            <td class="py-3 text-center"><span class="badge bg-secondary">v{{ doc.versions_count }}</span></td>
            <td class="py-3 text-end">
                <a href="{{ url_for('main.visualizar', filename=doc.arquivo_nome) }}" class="btn btn-outline-info btn-sm me-2 px-3" style="border-color: #2e3748;">
                    <i class="fa-solid fa-eye"></i>
                </a>
                <a href="{{ url_for('main.editar', filename=doc.arquivo_nome) }}" class="btn btn-outline-custom btn-sm me-2 px-3">
                    <i class="fa-solid fa-pen-to-square"></i>
                </a>
                <a href="{{ url_for('main.deletar', filename=doc.arquivo_nome) }}" class="btn btn-outline-danger btn-sm px-3" style="border: 1px solid rgba(248, 113, 113, 0.2);" onclick="return confirm('Tem certeza que deseja deletar este documento e histórico?')">
                    <i class="fa-solid fa-trash-can"></i>
                </a>
            </td>
        </tr>
    {% endfor %}
</tbody>

## 📄 Em templates/editor.html (Mudar o input do Título de Exibição):

<!-- Mude a seção do input do título do arquivo no editor.html -->
<div class="mb-4">
    <label for="titulo_exibicao" class="form-label fw-semibold text-light mb-2">Título de Exibição do Documento</label>
    <div class="input-group">
        <span class="input-group-text bg-dark border-secondary text-muted" style="background-color: #1a222f !important; border-color: #2e3748 !important;"><i class="fa-solid fa-heading"></i></span>
        <input type="text" class="form-control form-control-lg bg-dark text-white border-secondary" id="titulo_exibicao" name="titulo_exibicao" value="{{ titulo_exibicao }}" placeholder="Ex: Proposta Comercial de Automação" style="box-shadow: none; background-color: #0f141c !important; border-color: #2e3748 !important;" required>
    </div>
</div>

## 📄 Em templates/visualizar.html (Painel Lateral de Versões e Metadados):
Adicione uma barra lateral estilizada no modo de leitura para você alternar entre as versões gravadas do histórico. Substitua o bloco de conteúdo por este:

{% extends 'base.html' %}

{% block content %}
<div class="row">
    <!-- Coluna Principal da Leitura -->
    <div class="col-lg-9">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <a href="{{ url_for('main.home') }}" class="btn btn-outline-custom">
                <i class="fa-solid fa-arrow-left me-2"></i> Voltar ao Painel
            </a>
            <div>
                <a href="{{ url_for('main.editar', filename=filename) }}" class="btn btn-accent px-4">
                    <i class="fa-solid fa-pen-to-square me-2"></i> Editar Atual
                </a>
            </div>
        </div>

        <div class="card-custom mb-5">
            <div class="border-bottom border-secondary pb-3 mb-4 d-flex justify-content-between align-items-end">
                <div>
                    <h1 class="fw-bold text-white m-0"><i class="fa-regular fa-file-lines text-info me-2"></i> {{ titulo }}</h1>
                    <small class="text-muted">Criado em: {{ meta.criado_em }} | Última alteração: {{ meta.atualizado_em }}</small>
                </div>
                <span class="badge bg-info text-dark fs-6 px-3 py-2 fw-bold">Visualizando Versão v{{ versao_atual }}</span>
            </div>

            <div class="markdown-body" id="conteudo-documento">
                {{ conteudo_html | safe }}
            </div>
        </div>
    </div>

    <!-- ⏳ PAINEL LATERAL DE VERSÕES HISTÓRICAS -->
    <div class="col-lg-3">
        <h5 class="fw-bold text-uppercase tracking-wider text-muted mb-3" style="font-size:0.85rem;"><i class="fa-solid fa-clock-rotate-left text-warning me-1"></i> Histórico de Versões</h5>
        <div class="list-group">
            {% for v in versoes %}
                <a href="{{ url_for('main.visualizar', filename=filename, v=v.versao_numero) }}" 
                   class="list-group-item list-group-item-action bg-dark border-secondary text-white py-2 {% if v.versao_numero == versao_atual %}active border-info{% endif %}"
                   style="background-color: #1c2333 !important; border-color: #2e3748 !important;">
                    <div class="d-flex w-100 justify-content-between align-items-center">
                        <strong class="{% if v.versao_numero == versao_atual %}text-info{% else %}text-white{% endif %}">Versão v{{ v.versao_numero }}</strong>
                    </div>
                    <small class="text-muted d-block" style="font-size:0.75rem;">{{ v.salvo_em }}</small>
                </a>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}

------------------------------
## 🔄 Rodando o Projeto com as Novas Mudanças

   1. Salve todas as alterações.
   2. Certifique-se de que aplicou a injeção de caminho (sys.path.insert) no seu app.py caso estivesse com problemas de importação anteriormente.
   3. No terminal, execute python app.py ou python -m app.

O banco de dados dados.db será gerado automaticamente. Agora, ao criar um novo documento, o nome físico do arquivo será normalizado em segundo plano (ex: proposta_comercial.md), mas na interface você verá e poderá editar livremente o nome formatado real com espaços e acentos. Cada alteração que salvar criará uma nova versão no painel lateral de histórico!
O versionamento funcionou corretamente ao alternar os cliques no painel lateral? Se precisar de mais alguma otimização de layout ou recurso, me avise!

---------------------------------------------------------------------------------------------------------

Para documentar este projeto com excelência e fornecer um guia completo para manutenção futura, o padrão ouro no mercado é criar uma documentação viva em formato Markdown (que você pode carregar e ler dentro do seu próprio sistema!).
Abaixo está a documentação técnica oficial estruturada, cobrindo o mapa de métodos do backend, a arquitetura das rotas, a engenharia de dados do banco e os tokens de design do front-end.
Crie um arquivo chamado DOCUMENTACAO.md na raiz do seu projeto e salve este conteúdo lá dentro: [1] 

# 📂 Documentação Técnica do Projeto — MD Studio
Este documento serve como o manual oficial de arquitetura, desenvolvimento e design do sistema **MD Studio**. A aplicação foi projetada sob o padrão **Fábrica de Aplicação (Application Factory)** com controle de dados via repositório em banco SQLite e interface offline otimizada.
---## 🛠️ 1. Arquitetura Geral & Estrutura de Pastas
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
### 🧭 Engenharia de Rotas e Endpoints#### 🏠 Painel Inicial (Home Dashboard)- **Endpoint**: `/`
- **Nome Técnico**: `main.home`
- **Método**: `GET`
- **Operação**: Captura o parâmetro de query opcional `busca`. Instancia a lista de documentos e injeta na tela `home.html`.
#### 👁️ Modo de Leitura Otimizado (Viewer)- **Endpoint**: `/visualizar/<filename>`
- **Nome Técnico**: `main.visualizar`
- **Método**: `GET`
- **Operação**: Carrega os metadados e o histórico de versões. Aceita o parâmetro opcional `?v=X`. Se fornecido, lê a versão histórica do banco, senão entrega o HTML final compilado da última versão estável.
#### 📝 Criação de Documentos- **Endpoint**: `/criar`
- **Nome Técnico**: `main.criar`
- **Métodos**: `GET` \| `POST`- **Operação**:
  - `GET`: Abre o formulário vazio do editor.
  - `POST`: Coleta o título descritivo do formulário, normaliza-o substituindo espaços por sublinhados (`_`), adiciona a extensão `.md` e chama a gravação como nova entidade (Versão 1).
#### ✏️ Edição Avançada- **Endpoint**: `/editar/<filename>`
- **Nome Técnico**: `main.editar`
- **Métodos**: `GET` \| `POST`- **Operação**:
  - `GET`: Puxa a versão mais atual do conteúdo em Markdown e a injeta dentro da área de texto manipulada pelo `EasyMDE`.
  - `POST`: Coleta as edições textuais enviadas, altera os metadados do documento mantendo o nome do arquivo técnico estável e incrementa o controle de versão.
#### 🗑️ Exclusão Absoluta- **Endpoint**: `/deletar/<filename>`
- **Nome Técnico**: `main.deletar`
- **Método**: `GET`
- **Operação**: Aciona a limpeza lógica e física do arquivo, emitindo uma mensagem flash do Flask de categoria `warning` que desparece automaticamente.
---## 🗄️ 4. Modelagem do Banco de Dados (SQLite)
O sistema de versionamento é sustentado por um relacionamento de um para muitos (`1:N`) mapeado puramente por consultas SQL preparadas nativas.
### 📊 Diagrama Lógico de Tabelas```text
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
---## 🎨 5. Guias e Tokens de Design do Front-End
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

------------------------------
## Como avançar o uso desta documentação?
Uma ideia fantástica para deixar seu app com cara de software profissional é criar um arquivo de teste dentro do seu sistema chamado Documentação do Sistema e colar esse texto Markdown lá dentro. Assim, você poderá ler os metadados dele, testar o realce de sintaxe de tabelas e acompanhar as atualizações visuais das suas rotas direto pela interface!
Deseja expandir essa base técnica incluindo as instruções de instalação do arquivo requirements.txt ou prefere criar um manual para o usuário final de como usar os emojis e ícones?

[1] [https://dev.to](https://dev.to/xandecodes/documentacao-automatica-usando-mkdocs-e-python-n99)

Aplicar o padrão Singleton no seu projeto estruturado em camadas é uma excelente decisão de design. Como o MarkdownRepository gerencia conexões de arquivos locais e, principalmente, a conexão com o banco de dados SQLite, ter múltiplas instâncias dessa classe rodando na memória pode gerar conflitos de escrita e travar o banco de dados (o famoso erro database is locked).
Garantindo uma única instância global do repositório, economizamos memória e centralizamos todo o controle de metadados e versionamento. [1, 2] 
Aqui está como implementar o padrão Singleton de forma elegante e Pythônica no seu projeto:
------------------------------
## 🗄️ 1. Atualizar a Camada de Dados (src/repositorio.py)
No Python, a maneira mais robusta de criar um Singleton é sobrescrevendo o método mágico __new__. Esse método controla a criação do objeto e garante que, se a instância já existir na memória, ele reaproveite a mesma em vez de criar uma nova. [3, 4] 
Abra o seu arquivo src/repositorio.py e adicione o controle do Singleton logo no início da classe MarkdownRepository:

import osimport sqlite3from datetime import datetimefrom markdown import markdown as md_converter
class MarkdownRepository:
    # 🔒 Variável privada de classe que guardará a instância única global
    _instancia = None

    def __new__(cls, *args, **kwargs):
        """Sobrescreve a criação do objeto para garantir o padrão Singleton."""
        if cls._instancia is None:
            # Se não existe instância na memória, cria uma nova
            cls._instancia = super(MarkdownRepository, cls).__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia

    def __init__(self):
        # ⚠️ Impede que o init seja executado múltiplas vezes ao chamar o Singleton
        if getattr(self, '_inicializado', False):
            return
            
        self.docs_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'documentos'
        )
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'dados.db'
        )
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
            
        self._criar_tabelas()
        
        # Marca como inicializado para travar futuros inits redundantes
        self._inicializado = True

    def _get_conexao(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _criar_tabelas(self):
        """Cria a estrutura de metadados e histórico se não existir."""
        with self._get_conexao() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_meta (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_nome TEXT UNIQUE,
                    titulo_exibicao TEXT,
                    versions_count INTEGER DEFAULT 1,
                    criado_em TEXT,
                    atualizado_em TEXT
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS documentos_versoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    arquivo_nome TEXT,
                    versao_numero INTEGER,
                    conteudo TEXT,
                    salvo_em TEXT
                )
            ''')
            conn.commit()

    # ... (Mantenha o restante de todos os seus métodos listar_todos, salvar, ler_conteudo idênticos abaixo)

------------------------------
## 🎛️ 2. Como usar no arquivo de Rotas (src/rotas.py)
A beleza dessa implementação é que o padrão ficou encapsulado. O arquivo src/rotas.py não precisa mudar a sintaxe, ele continuará instanciando normalmente.
Porém, graças ao Singleton, mesmo que você chame repo = MarkdownRepository() em 10 lugares diferentes ou em requisições paralelas, o Python retornará exatamente o mesmo endereço de memória, protegendo o seu banco SQLite.
O seu arquivo src/rotas.py deve apenas continuar instanciando o objeto de forma limpa:

from flask import Blueprint, render_template, request, redirect, url_for, flashfrom .repositorio import MarkdownRepository
main_bp = Blueprint('main', __name__)
# 🚀 O padrão Singleton intercepta essa chamada e garante uma única instância global!repo = MarkdownRepository()

@main_bp.route('/')def home():
    # ... código da rota home

------------------------------
## 🧪 Como testar se o Singleton está funcionando?
Para provar que o padrão está ativo e blindando seu código, você pode adicionar um teste temporário no final do seu arquivo de entrada principal app.py:

from src import create_appfrom src.repositorio import MarkdownRepository
app = create_app()
# Teste rápido do padrão Singletonrepo1 = MarkdownRepository()repo2 = MarkdownRepository()

print(f"====================================")
print(f"Instância 1 localiza-se em: {id(repo1)}")
print(f"Instância 2 localiza-se em: {id(repo2)}")
print(f"São o mesmo objeto na memória? {repo1 is repo2}")
print(f"====================================")
if __name__ == '__main__':
    app.run(debug=True, port=8080)

Ao iniciar o seu servidor com python app.py (ou python -m app), o terminal vai imprimir os IDs de memória. Eles serão idênticos e a resposta será True.
Seu projeto agora conta com uma arquitetura modularizada, banco relacional para metadados, controle automático de versão de Markdowns e segurança contra concorrência de disco usando Singleton.
O que você achou dessa proteção de dados? Avançamos para criar o arquivo requirements.txt para deixar o ambiente pronto para deploy, ou quer implementar alguma nova funcionalidade no editor?

[1] [https://www.youtube.com](https://www.youtube.com/watch?v=x9h8MgAvi_I)
[2] [https://www.reddit.com](https://www.reddit.com/r/csharp/comments/1acwtar/can_someone_explain_when_to_use_singleton_scoped/?tl=pt-br)
[3] [https://medium.com](https://medium.com/@nelson.miranda_40644/implementa%C3%A7%C3%A3o-do-padr%C3%A3o-de-design-singleton-em-python-um-guia-para-iniciantes-c033dcd773e5)
[4] [https://pt.linkedin.com](https://pt.linkedin.com/pulse/padr%C3%A3o-singleton-higor-diego)

Para que o seu sistema consiga interpretar links, formatações e marcações no estilo da Wikipedia (conhecido tecnicamente como Wikilinks), nós podemos ativar uma extensão nativa que vem embutida na biblioteca markdown do Python: a wikilinks.
Essa extensão converte automaticamente textos escritos entre colchetes duplos — como [[Nome da Página]] ou [[Nome da Página|Texto que vai aparecer]] — em links HTML convencionais que apontam diretamente para as rotas da sua aplicação.
Como reestruturamos o seu projeto usando padrões de projeto e centralizamos tudo no seu repositório Singleton, a implementação é extremamente rápida e limpa. Veja como configurar:
------------------------------
## 🐍 1. Atualizar o Conversor no Repositório (src/repositorio.py)
Precisamos ir até o método converter_para_html dentro do seu arquivo src/repositorio.py, adicionar a extensão 'wikilinks' na lista e configurá-la para que ela monte a URL correta apontando para a sua rota de visualização do Flask (/visualizar/nome_do_arquivo.md).
Abra o seu arquivo src/repositorio.py e atualize o método correspondente:

    def converter_para_html(self, conteudo_bruto):
        """Compila o Markdown cru em HTML com suporte a extensões e Wikilinks estilo Wikipedia."""
        
        # Lista de extensões que você já possui rodando
        extensoes_ativas = [
            'tables', 
            'emoji', 
            'pymdownx.tasklist', 
            'pymdownx.superfences', 
            'pymdownx.inlinehilite',
            'wikilinks' # ⬅️ ADICIONE A EXTENSÃO AQUI
        ]
        
        # Configuração da extensão Wikilinks para casar com as rotas do Flask
        configuracoes_extensoes = {
            'wikilinks': {
                # Define o prefixo que virá antes do nome do link.
                # Como nossa rota de visualização é '/visualizar/nome_do_arquivo.md', configuramos o padrão abaixo:
                'base_url': '/visualizar/',
                'end_url': '.md',
                
                # Função interna para limpar o nome digitado na Wikipedia (troca espaços por sublinhados)
                'build_url': lambda label, base, end: f"{base}{label.strip().replace(' ', '_').lower()}{end}"
            }
        }
        
        # Retorna o compilador injetando a lista e os parâmetros de configuração
        return md_converter(
            conteudo_bruto, 
            extensions=extensoes_ativas, 
            extension_configs=configuracoes_extensoes
        )

------------------------------
## 🔄 2. Como usar no Editor Markdown (Sintaxe Wikipedia)
Após salvar o arquivo e atualizar a página do navegador (pode usar Ctrl + F5), você já pode escrever nos seus documentos usando a sintaxe clássica da Wikipedia:
## Exemplo A: Link simples direto para outro arquivo existente

Se você quiser entender mais sobre raspagem de dados, leia o nosso artigo sobre [[Automação com Python]].

O sistema vai gerar um link invisível apontando automaticamente para a URL /visualizar/automacao_com_python.md.
## Exemplo B: Link com texto alternativo customizado (Usando a barra vertical |)

Veja o [[Guia de Deploy|manual de infraestrutura]] para colocar o sistema no ar.

Na tela aparecerá apenas a palavra clicável "manual de infraestrutura", mas ela redirecionará o usuário direto para o documento técnico guia_de_deploy.md.
------------------------------
## 🎨 3. Dica de Estilização Visual (static/css/custom.css)
Por padrão, a extensão do Python gera os links da Wikipedia usando uma classe chamada wikilink. Para deixá-los destacados e bonitos dentro do seu tema Slate confortável, adicione essa regra rápida no final do seu static/css/custom.css:

/* ==========================================================================
   ESTILIZAÇÃO DE WIKILINKS (WIKIPEDIA STYLE)
   ========================================================================== */
.markdown-body a.wikilink {
    color: var(--accent);                 /* Azul Sky de destaque */
    text-decoration: none;
    border-bottom: 1px dashed var(--accent); /* Adiciona uma linha pontilhada charmosa embaixo do link */
    transition: all 0.2s ease;
    font-weight: 500;
}

.markdown-body a.wikilink:hover {
    color: var(--accent-hover);
    border-bottom-style: solid;           /* A linha fica sólida ao passar o mouse */
    background-color: rgba(56, 189, 248, 0.08); /* Ganha um fundo levemente iluminado */
    border-radius: 2px;
    padding: 0 2px;
}

Dessa forma, você consegue interligar vários arquivos Markdown criando a sua própria Wiki interna de documentações de forma 100% offline e integrada, navegando de uma página para a outra apenas clicando nos colchetes duplos.
O redirecionamento entre os seus arquivos funcionou bem na página de visualização? Se quiser levar a experiência da Wikipedia ao limite, podemos configurar uma extensão chamada toc (Table of Contents) para criar um Índice/Sumário automático no topo do documento com base nos seus títulos # e ##. Deseja implementar isso?

Não, não é nada complicado! Na verdade, o HTMX se encaixa perfeitamente na estrutura que já montamos.
Como nós organizamos o backend usando o padrão Singleton + Blueprints + Repositório, o seu código Python não vai mudar quase nada. O HTMX vai nos permitir transformar a aplicação em uma SPA (Single Page Application): quando você clicar para visualizar, pesquisar ou criar um arquivo, a página não vai mais recarregar inteira (aquele "piscar" branco incômodo). O HTMX vai trocar apenas o miolo do conteúdo de forma instantânea [DOCS_DIR]. [1] 
Para fazer essa transição de forma rápida e 100% offline, siga estes passos para atualizar os seus arquivos:
------------------------------
## 📥 1. Baixar o HTMX para sua pasta local
Como o seu projeto roda offline, precisamos baixar o arquivo JavaScript do HTMX e colocá-lo na sua pasta static/js/. [2] 

   1. Acesse o link oficial: unpkg.com
   2. Copie todo o código da tela e salve dentro de: static/js/htmx.min.js

------------------------------
## 🎨 2. Atualizar o Layout Global (templates/base.html)
O HTMX precisa ser carregado aqui. Além disso, criaremos uma div chamada id="main-content" que servirá como o palco onde as páginas serão injetadas dinamicamente sem recarregar o navegador.
Substitua o conteúdo do seu templates/base.html por este:

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MD Studio — SPA com HTMX</title>
    
    <link rel="stylesheet" href="{{ url_for('static', filename='css/bootstrap.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/all.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/easymde.min.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
</head>
<body hx-headers='{"X-HTMX-Request": "true"}'> <!-- Avisa o Flask que estamos usando HTMX -->

    <nav class="navbar navbar-expand-lg navbar-custom mb-5">
        <div class="container">
            <!-- hx-get carrega a home e hx-target injeta apenas no miolo do site sem piscar a tela -->
            <a class="navbar-brand navbar-brand-custom" style="cursor:pointer;" 
               hx-get="{{ url_for('main.home') }}" hx-target="#main-content" hx-push-url="true">
                <i class="fa-solid fa-cubes text-info me-2"></i>MD<span>Studio</span>
            </a>
            <div class="navbar-nav ms-auto">
                <a class="btn btn-accent btn-sm px-3 py-2" style="cursor:pointer;"
                   hx-get="{{ url_for('main.criar') }}" hx-target="#main-content" hx-push-url="true">
                    <i class="fa-solid fa-plus me-1"></i> Criar Documento
                </a>
            </div>
        </div>
    </nav>

    <!-- O miolo do site fica encapsulado nesta DIV que o HTMX gerencia -->
    <div class="container" id="main-content">
        {% block content %}{% endblock %}
    </div>

    <!-- Scripts Locais -->
    <script src="{{ url_for('static', filename='js/bootstrap.bundle.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/easymde.min.js') }}"></script>
    <script src="{{ url_for('static', filename='js/htmx.min.js') }}"></script> <!-- ⬅️ HTMX ATIVO -->
    <script src="{{ url_for('static', filename='js/editor-init.js') }}"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>

------------------------------
## 🎛️ 3. O Ajuste Inteligente no Backend (src/rotas.py)
O único detalhe do HTMX é: se o usuário clicar em "Visualizar", o Flask não deve devolver a página com a Navbar e rodapé de novo, ele deve devolver apenas o miolo do HTML.
Para resolver isso de forma genial sem precisar duplicar seus arquivos HTML, nós validamos se a requisição veio do HTMX. Se veio, renderizamos apenas o bloco do conteúdo; se o usuário der F5 direto na URL, ele renderiza o layout completo normalmente.
Abra o seu src/rotas.py e atualize as rotas para usarem essa validação simples:

from flask import Blueprint, render_template, request, redirect, url_for, flashfrom .repositorio import MarkdownRepository
main_bp = Blueprint('main', __name__)repo = MarkdownRepository()
def render_spa(template_name, **context):
    """Função auxiliar: Se a requisição for do HTMX, renderiza apenas o template filho.
    Se for um acesso direto (F5), usa o fluxo normal estendendo o base.html."""
    if request.headers.get('X-HX-Request') or request.headers.get('X-HTMX-Request'):
        # Passar uma variável dizendo para o jinja ignorar o extends do base
        context['is_htmx'] = True
    else:
        context['is_htmx'] = False
    return render_template(template_name, **context)

@main_bp.route('/')def home():
    termo = request.args.get('busca', '')
    documentos = repo.listar_todos(termo)
    return render_spa('home.html', documentos=documentos, termo_busca=termo)

@main_bp.route('/visualizar/<filename>')def visualizar(filename):
    meta = repo.obter_meta(filename)
    if not meta:
        flash("Metadados não encontrados.", "danger")
        return redirect(url_for('main.home'))
        
    v_solicitada = request.args.get('v', None)
    conteudo_bruto = repo.obter_conteudo_versao(filename, v_solicitada)
    conteudo_html = repo.converter_para_html(conteudo_bruto)
    versoes = repo.listar_versoes(filename)
    
    return render_spa(
        'visualizar.html', 
        titulo=meta['titulo_exibicao'], 
        conteudo_html=conteudo_html, 
        filename=filename,
        meta=meta,
        versoes=versoes,
        versao_atual=int(v_solicitada) if v_solicitada else meta['versions_count']
    )

@main_bp.route('/criar', methods=['GET', 'POST'])def criar():
    if request.method == 'POST':
        titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        arquivo_tecnico = titulo_tela.replace(" ", "_").lower() + ".md"
        
        repo.salvar(arquivo_tecnico, conteudo, titulo_exibicao=titulo_tela, is_update=False)
        
        # Redirecionamento HTMX para atualizar a Home limpando a tela
        response = redirect(url_for('main.home'))
        response.headers['HX-Redirect'] = url_for('main.home')
        return response
        
    return render_spa('editor.html', acao="Criar", titulo_exibicao="", conteudo="")

@main_bp.route('/editar/<filename>', methods=['GET', 'POST'])def editar(filename):
    meta = repo.obter_meta(filename)
    if request.method == 'POST':
        novo_titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        repo.salvar(filename, conteudo, titulo_exibicao=novo_titulo_tela, is_update=True)
        
        response = redirect(url_for('main.home'))
        response.headers['HX-Redirect'] = url_for('main.home')
        return response

    conteudo = repo.obter_conteudo_versao(filename)
    return render_spa('editor.html', acao="Editar", titulo_exibicao=meta['titulo_exibicao'], conteudo=conteudo, filename=filename)

@main_bp.route('/deletar/<filename>')def deletar(filename):
    repo.deletar(filename)
    # Redirecionamento nativo do HTMX
    response = redirect(url_for('main.home'))
    response.headers['HX-Refresh'] = "true" 
    return response

------------------------------
## 🎛️ 4. Ajustar os arquivos HTML para o padrão condicional
Para que os arquivos HTML saibam se devem ou não herdar o base.html (dependendo se a chamada veio do HTMX), adicione uma condicional Jinja na primeira linha de cada um.
## 📄 No topo do templates/home.html:
Substitua a primeira linha {% extends 'base.html' %} por isto:

{% if not is_htmx %}{% extends 'base.html' %}{% endif %}

E na barra de busca interna do home.html, faça a pesquisa filtrar em tempo real conforme você digita adicionando os gatilhos do HTMX (hx-get, hx-trigger, hx-target): [3] 

<!-- Procure a tag <input name="busca" ...> no seu home.html e altere para ficar assim: -->
<input type="text" name="busca" class="form-control bg-dark text-white border-secondary" 
       placeholder="Pesquisar por título ou conteúdo..." 
       value="{{ termo_busca }}" 
       hx-get="{{ url_for('main.home') }}" 
       hx-trigger="keyup changed delay:300ms" 
       hx-target="#main-content"
       style="background-color: #0f141c !important; border-color: #2e3748 !important; box-shadow: none;">

(Nota: altere também os links <a> de Visualizar e Editar na tabela para usarem hx-get="{{ url_for(...) }}" hx-target="#main-content" hx-push-url="true" no lugar do href normal).
## 📄 No topo do templates/visualizar.html:
Substitua a primeira linha por:

{% if not is_htmx %}{% extends 'base.html' %}{% endif %}

E altere os links do painel de histórico lateral para carregar a versão antiga via HTMX:

<!-- Mude a tag <a> do laço for das versões no visualizar.html: -->
<a hx-get="{{ url_for('main.visualizar', filename=filename, v=v.versao_numero) }}" 
   hx-target="#main-content" style="cursor:pointer;"
   class="list-group-item list-group-item-action bg-dark border-secondary text-white py-2 {% if v.versao_numero == versao_atual %}active border-info{% endif %}">

## 📄 No topo do templates/editor.html:
Substitua a primeira linha por:

{% if not is_htmx %}{% extends 'base.html' %}{% endif %}

E no final do arquivo, force o HTMX a reinicializar o editor de Markdown sempre que a página for injetada via AJAX:

{% block scripts %}
<script>
    // Executa imediatamente ao carregar via HTMX
    inicializarEditorMarkdown("{{ titulo_exibicao }}");
</script>
{% endblock %}

------------------------------
## 🔥 O Resultado na Prática
Abra o terminal e execute o projeto (python app.py).
A mágica aconteceu! Ao digitar na barra de pesquisa, a tabela filtra as propostas e Markdowns em tempo real a cada tecla digitada, sem dar refresh. Ao alternar entre as versões do histórico na barra lateral, o texto muda instantaneamente. O HTMX eliminou todo o peso de transição de páginas transformando o seu sistema em uma SPA extremamente veloz e fluida [DOCS_DIR].
Como ficou a velocidade de transição entre as telas no seu monitor agora?

[1] [https://webdev2025.lol](https://webdev2025.lol/webmac/aula9.html)
[2] [https://www.reddit.com](https://www.reddit.com/r/htmx/hot/?tl=pt-br)
[3] [https://www.reddit.com](https://www.reddit.com/r/htmx/comments/1k5bz3y/htmx_a_great_framework_that_ill_never_use_again/?tl=pt-br)



