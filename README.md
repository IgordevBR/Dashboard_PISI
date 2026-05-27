# Playscope Dashboard 🎮

Plataforma analítica interativa do mercado Steam — desenvolvida com **Dash + Plotly + Pandas**.

---

## Estrutura do Projeto

```
playscope_dashboard/
├── dashboard.py              ← ponto de entrada (execute este arquivo)
├── requirements.txt
├── generate_demo_data.py     ← gera os datasets a partir do CSV real ou demo
├── data/
│   ├── steam_dashboard.parquet   ← dataset principal (50.872 jogos)
│   ├── cluster_profile.parquet   ← perfil médio dos 4 clusters
│   ├── shap_importance.parquet   ← importância SHAP das features
│   └── model_results.parquet     ← comparação dos modelos supervisionados
├── assets/
│   └── style.css             ← tema dark Steam
├── layouts/                  ← estrutura de cada página (sem lógica)
│   ├── sidebar.py
│   ├── overview.py
│   ├── engagement.py
│   ├── clusters.py
│   ├── pricing.py
│   └── shap_page.py
├── callbacks/                ← toda a lógica interativa
│   ├── theme.py
│   ├── overview_cb.py
│   ├── engagement_cb.py
│   ├── cluster_cb.py
│   ├── pricing_cb.py
│   ├── shap_cb.py
│   └── reset_cb.py
└── utils/
    └── data_loader.py        ← carregamento com cache (lru_cache)
```

---

## Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior
- pip atualizado

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Execute o dashboard
```bash
python dashboard.py
```

### 5. Acesse no navegador
```
http://127.0.0.1:8050
```

## Páginas do Dashboard

| Página | Descrição |
|--------|-----------|
| 📊 **Visão Geral** | KPIs, distribuição de preços, avaliações, top gêneros, scatter de reviews, heatmap de correlação de Spearman |
| 🎮 **Engajamento** | Horas jogadas vs. revenue, boxplot por gênero, preço vs. horas, comparativo Steam Deck, lançamentos por ano |
| 🔬 **Clusterização** | PCA 2D interativo, radar chart comparativo, perfis dos clusters, taxa de sucesso, tags por cluster |
| 💰 **Mercado & Preços** | Preço vs. reviews, revenue por faixa de preço, desconto vs. revenue, violino por cluster, top 20 jogos |
| 🧠 **Interpretabilidade** | SHAP bar plot, comparação de modelos, SHAP summary dot plot, dependence plots, matriz de confusão |

---

## Filtros Globais (Sidebar)

Todos os gráficos respondem dinamicamente aos filtros:

- **Gênero / Tag** — filtra por tag primária
- **Faixa de preço** — slider de $0 a $250
- **Avaliação mínima** — positive ratio mínimo
- **Ano de lançamento** — range de 2003 a 2024
- **Clusters** — seleciona quais clusters exibir
- **Steam Deck** — compatível / incompatível / todos
- **Sucesso Comercial** — top 20% / resto / todos

---

## Tecnologias

- **Dash 2.17** — framework de aplicações analíticas
- **Plotly 5.22** — visualizações interativas
- **Pandas 2.2** — manipulação de dados
- **PyArrow** — formato Parquet (alta performance)
- **Scikit-learn** — PCA e KMeans (pré-processamento)
