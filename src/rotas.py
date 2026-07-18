from flask import Blueprint, render_template, request, redirect, url_for, flash
from .repositorio import MarkdownRepository

main_bp = Blueprint('main', __name__)
repo = MarkdownRepository()

@main_bp.route('/')
def home():
    termo = request.args.get('busca', '')
    documentos = repo.listar_todos(termo) # Retorna dicionários do banco com os títulos customizados
    return render_template('home.html', documentos=documentos, termo_busca=termo)

@main_bp.route('/visualizar/<filename>')
def visualizar(filename):
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

@main_bp.route('/criar', methods=['GET', 'POST'])
def criar():
    if request.method == 'POST':
        titulo_tela = request.form.get('titulo_exibicao').strip()
        conteudo = request.form.get('conteudo')
        
        # Cria um nome de arquivo seguro em disco baseado no título
        arquivo_tecnico = titulo_tela.replace(" ", "_").lower() + ".md"
        
        repo.salvar(arquivo_tecnico, conteudo, titulo_exibicao=titulo_tela, is_update=False)
        flash(f"Documento '{titulo_tela}' criado com sucesso!", "success")
        return redirect(url_for('main.home'))
        
    return render_template('editor.html', acao="Criar", titulo_exibicao="", conteudo="")

@main_bp.route('/editar/<filename>', methods=['GET', 'POST'])
def editar(filename):
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

@main_bp.route('/deletar/<filename>')
def deletar(filename):
    repo.deletar(filename)
    flash("Documento e todo o seu histórico foram removidos.", "warning")
    return redirect(url_for('main.home'))
