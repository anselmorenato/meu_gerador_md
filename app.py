from src import create_app
from src.repositorio import MarkdownRepository

app = create_app()

# Teste rápido do padrão Singleton
repo1 = MarkdownRepository()
repo2 = MarkdownRepository()

print(f"====================================")
print(f"Instância 1 localiza-se em: {id(repo1)}")
print(f"Instância 2 localiza-se em: {id(repo2)}")
print(f"São o mesmo objeto na memória? {repo1 is repo2}")
print(f"====================================")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)