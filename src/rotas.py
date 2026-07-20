from flask import Blueprint, render_template, request, redirect, url_for, flash
from .repositorio import MarkdownRepository

main_bp = Blueprint('main', __name__)
repo = MarkdownRepository()

def render_spa(template_name, **context):
    """Função auxiliar que valida se a requisição veio do HTMX para injetar 
    corretamente blocos parciais e headers dinâmicos (OOB)."""
    if request.headers.get('X-HX-Request') or request.headers.get('X-HTMX-Request'):
        context['is_htmx'] = True
    else:
        context['is_htmx'] = False
    return render_template(template_name, **context)

@main_bp.route('/')
def home():
    termo = request.args.get('busca', '')
    documentos = repo.listar_todos(termo) # Retorna dicionários do banco com os títulos customizados
    return render_spa('home.html', documentos=documentos, termo_busca=termo)

@main_bp.route('/visualizar/<filename>')
def visualizar(filename):
    meta = repo.obter_meta(filename)
    if not meta:
        flash("Metadados não encontrados.", "danger")
        return redirect(url_for('main.home'))
        
    v_solicitada = request.args.get('v', None)
    conteudo_bruto = repo.obter_conteudo_versao(filename, v_solicitada)
    
    # 🔄 ATUALIZADO: Recebe também o dicionário contendo os metadados do YAML
    conteudo_html, sumario_html, meta_yaml = repo.converter_para_html(conteudo_bruto)
    
    versoes = repo.listar_versoes(filename)
    
    return render_spa(
        'visualizar.html', 
        titulo=meta['titulo_exibicao'], 
        conteudo_html=conteudo_html, 
        sumario_html=sumario_html,
        meta_yaml=meta_yaml, # ⬅️ Envia para a tela
        filename=filename,
        meta=meta,
        versoes=versoes,
        versao_atual=int(v_solicitada) if v_solicitada else meta['versions_count']
    )

@main_bp.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        
        # Cria um nome de arquivo seguro em disco baseado no título
        arquivo_tecnico = titulo_tela.replace(" ", "_").lower() + ".md"
        
        repo.salvar(arquivo_tecnico, conteudo, titulo_exibicao=titulo_tela, is_update=False)
        #flash(f"Documento '{titulo_tela}' criado com sucesso!", "success")
        return redirect(url_for('main.home'))
        response.headers['HX-Redirect'] = url_for('main.home')
        return response
        
    return render_template('editor.html', acao="Criar", titulo_exibicao="", conteudo="")

@main_bp.route('/editar/<filename>', methods=['GET', 'POST'])
def editar(filename):
    meta = repo.obter_meta(filename)
    
    #if not meta:
        #flash("Arquivo não encontrado.", "danger")
        #return redirect(url_for('main.home'))

    if request.method == 'POST':
        novo_titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        
        repo.salvar(filename, conteudo, titulo_exibicao=novo_titulo_tela, is_update=True)
        #flash(f"Documento '{novo_titulo_tela}' atualizado com uma nova versão!", "success")
        #return redirect(url_for('main.home'))
        response = redirect(url_for('main.home'))
        response.headers['HX-Redirect'] = url_for('main.home')
        return response

    conteudo = repo.obter_conteudo_versao(filename)
    return render_template('editor.html', acao="Editar", titulo_exibicao=meta['titulo_exibicao'], conteudo=conteudo, filename=filename)

@main_bp.route('/deletar/<filename>')
def deletar(filename):
    repo.deletar(filename)
    #flash("Documento e todo o seu histórico foram removidos.", "warning")
    #return redirect(url_for('main.home'))
     # Redirecionamento nativo do HTMX
    response = redirect(url_for('main.home'))
    response.headers['HX-Refresh'] = "true" 
    return response