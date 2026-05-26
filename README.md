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

---

## Usando seus dados reais

Se você possui os arquivos originais do Kaggle (`games.csv`, `recommendations.csv`, `games_metadata.json`), basta:

1. Colocar os três arquivos na raiz do projeto (mesmo nível de `dashboard.py`)
2. Editar `generate_demo_data.py` — substituir a geração sintética pela leitura real:

```python
import pandas as pd, json, numpy as np, os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

DATA_DIR = 'data'
os.makedirs(DATA_DIR, exist_ok=True)

# Carrega dados reais
df_games = pd.read_csv('games.csv')
df_games.columns = df_games.columns.str.strip().str.lower()

# Engagement
df_recom = pd.read_csv('recommendations.csv', usecols=['app_id', 'hours'])
df_eng = df_recom.groupby('app_id').agg(avg_hours=('hours','mean')).reset_index()
df = df_games.merge(df_eng, on='app_id', how='left')
df['avg_hours'] = df['avg_hours'].fillna(0)

# Tags
app_tags = {}
with open('games_metadata.json') as f:
    for line in f:
        row = json.loads(line)
        app_tags[row['app_id']] = row.get('tags', [])
df['tags_str']    = df['app_id'].map(lambda x: '|'.join(app_tags.get(x, [])))
df['primary_tag'] = df['tags_str'].str.split('|').str[0]

# Engenharia
df = df[df['user_reviews'] >= 100].copy()
df['est_revenue_proxy'] = df['price_final'] * df['user_reviews']
df['commercial_success'] = (df['est_revenue_proxy'] >= df['est_revenue_proxy'].quantile(0.80)).astype(int)
df['year'] = pd.to_datetime(df['date_release'], errors='coerce').dt.year

# KMeans K=4
feat = np.column_stack([
    np.log1p(df['avg_hours']),
    df['positive_ratio'] / 100,
    np.log1p(df['est_revenue_proxy']),
    df['discount'] / 100,
])
scaler = StandardScaler()
feat_s = scaler.fit_transform(feat)
km = KMeans(n_clusters=4, random_state=42, n_init=10)
df['cluster'] = km.fit_predict(feat_s)

# PCA
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(feat_s)
df['pca_x'], df['pca_y'] = coords[:,0], coords[:,1]

df.to_parquet('data/steam_dashboard.parquet', index=False)
print("Dataset real salvo!")
```

3. Execute: `python generate_demo_data.py`
4. Execute: `python dashboard.py`

---

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
