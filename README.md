# Envio de Ofertas

Sistema de divulgação de ofertas de supermercado em formato Stories.

- **Site público**: Visualização vertical de ofertas (como Stories) hospedado em GitHub Pages
- **Painel administrativo**: Interface desktop Python para gerenciar ofertas
- **Publicação com 1 clique**: Gera o site estático e publica automaticamente via Git

## Requisitos

- **Python 3.10+**
- **Git** instalado e configurado
- Dependências Python: `pip install -r requirements.txt`

## Estrutura do Projeto

```
envio_de_ofertas/
├── admin/          # Painel administrativo Python
│   ├── core/       # Configurações, caminhos, validadores, Git
│   ├── models/     # Modelo de dados (Offer)
│   ├── services/   # Regras de negócio
│   └── ui/         # Interface gráfica
├── config/         # Configurações do site e publicação
├── data/           # Dados mestres (offers.json)
├── ofertas/        # Imagens originais e otimizadas
├── scripts/        # Automação (build, otimização)
├── site/           # Site público gerado
├── templates/      # Moldes HTML, JSON, XML
└── tests/          # Testes unitários
```

## Como Usar

### 1. Preparar o ambiente

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### 2. Configurar

Edite `config/site.json` com os dados do seu site e `config/publishing.json` com a URL do repositório remoto.

### 3. Iniciar o painel administrativo

```bash
python -m admin.app
```

### 4. Publicar

No painel, clique em **Publicar Site**. O sistema vai:
1. Gerar os arquivos estáticos em `site/`
2. Executar `git add`, `git commit` e `git push`

## Tecnologias

- **Frontend público**: HTML5, CSS3, JavaScript puro
- **Painel admin**: Python + CustomTkinter
- **Persistência**: JSON + sistema de arquivos
- **Hospedagem**: GitHub Pages / Cloudflare Pages

## Licença

MIT
