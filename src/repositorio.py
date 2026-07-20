import os
import sqlite3
from datetime import datetime
from markdown import Markdown, markdown as md_converter



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
        """Compila o Markdown extraindo metadados YAML (front-matter) e gerando o TOC."""
        
        extensoes_ativas = [
            'tables', 
            'pymdownx.emoji', 
            'pymdownx.tasklist', 
            'pymdownx.superfences', 
            'pymdownx.inlinehilite',
            'wikilinks',
            'toc',
            'markdown.extensions.meta' # ⬅️ ADICIONE ESTA EXTENSÃO NATIVA AQUI
        ]
        
        configuracoes_extensoes = {
            'wikilinks': {
                'base_url': '/visualizar/',
                'end_url': '.md',
                'build_url': lambda label, base, end: f"{base}{label.strip().replace(' ', '_').lower()}{end}"
            },
            'toc': {
                'baselevel': 1,
                'marker': '[TOC]'
            }
        }
        
        #from markdown import Markdown
        md = Markdown(extensions=extensoes_ativas, extension_configs=configuracoes_extensoes)
        
        conteudo_html = md.convert(conteudo_bruto)
        sumario_html = md.toc
        
        # 🎣 Captura os metadados do front-matter processados pela extensão
        # Os valores retornam sempre como listas no Python-Markdown, por isso tratamos abaixo:
        meta_yaml = getattr(md, 'Meta', {})
        
        metadados_tratados = {
            'autor': meta_yaml.get('autor', [''])[0] or meta_yaml.get('author', [''])[0],
            'tags': [t.strip() for t in meta_yaml.get('tags', [''])[0].split(',')] if meta_yaml.get('tags') else []
        }
        
        return conteudo_html, sumario_html, metadados_tratados
