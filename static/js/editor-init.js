// Função global para ligar o editor avançado no textarea
function inicializarEditorMarkdown(tituloDocumento) {
    const elementoTextarea = document.getElementById('conteudo');
    if (!elementoTextarea) return;

    return new EasyMDE({
        element: elementoTextarea,
        spellChecker: false,
        autosave: {
            enabled: false 
        },
        renderingConfig: {
            singleLineBreaks: false, // Força o padrão do Markdown clássico (evita pular linha duplo)
            codeSyntaxHighlighting: false,
        },
        // Força o CodeMirror a não injetar margens extras nos blocos de parágrafo
        forceSync: true, 
        toolbar: [
            "bold", "italic", "heading", "|", 
            "quote", "unordered-list", "ordered-list", "|", 
            "link", "image", "|", 
            "preview", "side-by-side", "fullscreen"
        ],
        placeholder: "Construa sua documentação aqui...",
    });
}

// Auto fechar os alertas toast após 4 segundos
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        let alerts = document.querySelectorAll('.alert-floating');
        alerts.forEach(alert => {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                let bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 4000);
});
