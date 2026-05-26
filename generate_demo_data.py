"""
Gera o dataset sintético para demo do Playscope Dashboard.
Estatísticas fiéis ao notebook real (Pisi3_Grupo6_2026_1.ipynb):
  - 50.872 jogos, 4 clusters KMeans (K=4)
  - Cluster 0: 11204 | Cluster 1: 20133 | Cluster 2: 15807 | Cluster 3: 3728
  - SHAP top features: rating_Positive > avg_hours > positive_ratio
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import os, warnings
warnings.filterwarnings('ignore')

np.random.seed(42)
N = 50872
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# ── Cluster sizes ──────────────────────────────────────────────────────────────
CLUSTER_SIZES = {0: 11204, 1: 20133, 2: 15807, 3: 3728}
CLUSTER_NAMES = {
    0: "Alto Faturamento Estimado",
    1: "Boa Avaliação, Baixo Alcance",
    2: "Alto Engajamento e Sucesso",
    3: "Alta Estratégia Promocional"
}

# ── Tags pool ──────────────────────────────────────────────────────────────────
TOP_TAGS = ['Indie','Action','Adventure','Casual','Singleplayer',
            'Strategy','Simulation','RPG','Atmospheric','2D']
ALL_TAGS  = TOP_TAGS + ['Horror','Puzzle','Racing','Sports','FPS',
                        'Multiplayer','Co-op','Open World','Survival',
                        'Fantasy','Sci-fi','Platformer','Roguelike','Tower Defense']

RATINGS = ['Overwhelmingly Positive','Very Positive','Mostly Positive',
           'Positive','Mixed','Mostly Negative','Very Negative','Overwhelmingly Negative']
RATING_WEIGHTS = [0.05, 0.28, 0.20, 0.22, 0.15, 0.05, 0.03, 0.02]

# ── Publishers ─────────────────────────────────────────────────────────────────
PUBLISHERS = ['Valve','Electronic Arts','Ubisoft','Activision','Bethesda',
              'CD Projekt','2K Games','Square Enix','Bandai Namco','SEGA',
              'Paradox Interactive','THQ Nordic','Focus Entertainment',
              'Team17','Devolver Digital','Raw Fury','Annapurna Interactive',
              'Coffee Stain Studios','Double Fine','Humble Games'] + \
             [f'Indie Studio {i}' for i in range(1, 81)]

def gen_cluster_data(cid, n):
    """Generate per-cluster features matching notebook medians."""
    rng = np.random.RandomState(42 + cid)

    if cid == 0:   # Alto Faturamento — low approval, medium hours, varied revenue
        pos_ratio   = np.clip(rng.normal(54, 20, n), 10, 100)
        avg_hours   = np.clip(np.exp(rng.normal(np.log(2.0), 1.2, n)), 0.1, 500)
        rev_proxy   = np.clip(np.exp(rng.normal(np.log(115), 2.5, n)), 1, 5e7)
        discount    = np.clip(rng.exponential(5, n), 0, 60)
        price       = np.clip(rng.lognormal(2.5, 0.8, n), 0, 200)

    elif cid == 1: # Boa Avaliação — high approval, very low hours, tiny revenue
        pos_ratio   = np.clip(rng.normal(88, 7, n), 60, 100)
        avg_hours   = np.clip(np.exp(rng.normal(np.log(0.5), 1.0, n)), 0.01, 50)
        rev_proxy   = np.clip(np.exp(rng.normal(np.log(68), 1.8, n)), 1, 1e6)
        discount    = np.clip(rng.exponential(3, n), 0, 40)
        price       = np.clip(rng.lognormal(1.5, 1.1, n), 0, 60)

    elif cid == 2: # Alto Engajamento — high approval, high hours, high revenue
        pos_ratio   = np.clip(rng.normal(85, 8, n), 55, 100)
        avg_hours   = np.clip(np.exp(rng.normal(np.log(14.8), 1.5, n)), 0.5, 2000)
        rev_proxy   = np.clip(np.exp(rng.normal(np.log(1976), 2.0, n)), 10, 2e8)
        discount    = np.clip(rng.exponential(8, n), 0, 50)
        price       = np.clip(rng.lognormal(2.8, 0.9, n), 0, 250)

    else:          # Alta Estratégia Promocional — moderate approval, heavy discounts
        pos_ratio   = np.clip(rng.normal(80, 10, n), 40, 100)
        avg_hours   = np.clip(np.exp(rng.normal(np.log(3.7), 1.3, n)), 0.1, 200)
        rev_proxy   = np.clip(np.exp(rng.normal(np.log(61), 2.0, n)), 1, 5e5)
        discount    = np.clip(rng.normal(70, 15, n), 30, 95)
        price       = np.clip(rng.lognormal(2.0, 1.0, n), 0, 80)

    user_reviews = np.clip((rev_proxy / np.maximum(price, 0.01)).astype(int), 0, 5_000_000)
    return pos_ratio, avg_hours, rev_proxy, discount, price, user_reviews

# ── Build rows per cluster ─────────────────────────────────────────────────────
rows = []
app_id_counter = 10000

for cid, n in CLUSTER_SIZES.items():
    pos_ratio, avg_hours, rev_proxy, discount, price_final, user_reviews = gen_cluster_data(cid, n)
    rng = np.random.RandomState(100 + cid)

    for i in range(n):
        pr = price_final[i]
        po = pr / (1 - discount[i]/100) if discount[i] < 100 else pr
        yr = int(rng.choice(range(2003, 2025),
                            p=np.array([1,1,1,1,2,2,3,4,5,6,8,9,10,11,12,10,8,7,5,4,3,2])/115))
        mo = rng.randint(1,13)
        da = rng.randint(1,29)
        date = f"{yr}-{mo:02d}-{da:02d}"

        rating = rng.choice(RATINGS, p=RATING_WEIGHTS)
        if pos_ratio[i] >= 95: rating = 'Overwhelmingly Positive'
        elif pos_ratio[i] >= 85: rating = rng.choice(['Very Positive','Mostly Positive'])
        elif pos_ratio[i] >= 70: rating = rng.choice(['Mostly Positive','Positive'])
        elif pos_ratio[i] >= 50: rating = 'Mixed'
        else: rating = rng.choice(['Mostly Negative','Very Negative'])

        tag1 = rng.choice(TOP_TAGS)
        extra = list(rng.choice(ALL_TAGS, size=rng.randint(1,5), replace=False))
        tags  = list(dict.fromkeys([tag1] + extra))

        rows.append({
            'app_id':           app_id_counter,
            'title':            f"Game {app_id_counter}",
            'date_release':     date,
            'win':              True,
            'mac':              bool(rng.random() < 0.25),
            'linux':            bool(rng.random() < 0.20),
            'rating':           rating,
            'positive_ratio':   round(pos_ratio[i], 1),
            'user_reviews':     int(user_reviews[i]),
            'price_final':      round(pr, 2),
            'price_original':   round(po, 2),
            'discount':         round(discount[i], 1),
            'steam_deck':       bool(rng.random() < 0.60),
            'avg_hours':        round(avg_hours[i], 2),
            'est_revenue_proxy':round(rev_proxy[i], 2),
            'cluster':          cid,
            'cluster_name':     CLUSTER_NAMES[cid],
            'primary_tag':      tag1,
            'tags_str':         '|'.join(tags),
            'year':             yr,
            'publisher':        rng.choice(PUBLISHERS),
        })
        app_id_counter += 1

df = pd.DataFrame(rows)

# ── commercial_success (top 20%) ───────────────────────────────────────────────
threshold = df['est_revenue_proxy'].quantile(0.80)
df['commercial_success'] = (df['est_revenue_proxy'] >= threshold).astype(int)

# ── PCA coordinates ────────────────────────────────────────────────────────────
import numpy as np
feat_pca = np.column_stack([
    np.log1p(df['avg_hours'].values),
    df['positive_ratio'].values / 100,
    np.log1p(df['est_revenue_proxy'].values),
    df['discount'].values / 100,
])
scaler = StandardScaler()
feat_scaled = scaler.fit_transform(feat_pca)
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(feat_scaled)
df['pca_x'] = coords[:, 0]
df['pca_y'] = coords[:, 1]
print(f"PCA variance explained: PC1={pca.explained_variance_ratio_[0]:.1%}, PC2={pca.explained_variance_ratio_[1]:.1%}")

# ── Save main dataset ──────────────────────────────────────────────────────────
df['date_release'] = pd.to_datetime(df['date_release'])
df.to_parquet(os.path.join(DATA_DIR, 'steam_dashboard.parquet'), index=False)
print(f"steam_dashboard.parquet saved: {len(df):,} rows, {df.shape[1]} cols")

# ── Cluster profile ────────────────────────────────────────────────────────────
profile = df.groupby(['cluster','cluster_name']).agg(
    count             =('app_id','count'),
    avg_hours_mean    =('avg_hours','mean'),
    avg_hours_median  =('avg_hours','median'),
    positive_ratio_mean=('positive_ratio','mean'),
    positive_ratio_median=('positive_ratio','median'),
    est_revenue_proxy_mean=('est_revenue_proxy','mean'),
    est_revenue_proxy_median=('est_revenue_proxy','median'),
    discount_mean     =('discount','mean'),
    discount_median   =('discount','median'),
    commercial_success_rate=('commercial_success','mean'),
).reset_index()
profile.to_parquet(os.path.join(DATA_DIR, 'cluster_profile.parquet'), index=False)
print("cluster_profile.parquet saved")

# ── SHAP importance (from notebook article results) ────────────────────────────
shap_data = pd.DataFrame({
    'feature':    ['rating_Positive','avg_hours','positive_ratio',
                   'rating_Very Positive','rating_Overwhelmingly Positive',
                   'discount','rating_Negative','rating_Very Negative',
                   'rating_Overwhelmingly Negative','rating_Mostly Negative',
                   'rating_Mostly Positive','steam_deck_True'],
    'importance': [1.12, 0.95, 0.40, 0.15, 0.10,
                   0.08, 0.04, 0.02, 0.01, 0.01, 0.01, 0.005],
    'feature_label': ['Rating: Positive','Média de Horas Jogadas','Taxa de Aprovação (%)',
                      'Rating: Very Positive','Rating: Overwhelmingly Positive',
                      'Desconto (%)','Rating: Negative','Rating: Very Negative',
                      'Rating: Overwhelmingly Negative','Rating: Mostly Negative',
                      'Rating: Mostly Positive','Steam Deck Compatível']
})
shap_data.to_parquet(os.path.join(DATA_DIR, 'shap_importance.parquet'), index=False)
print("shap_importance.parquet saved")

# ── Model comparison ───────────────────────────────────────────────────────────
model_results = pd.DataFrame({
    'modelo':    ['Gradient Boosting','Regressão Logística','Random Forest','SVM (Linear)'],
    'acuracia':  [0.7835, 0.7521, 0.7658, 0.6636],
    'precisao':  [0.4758, 0.4326, 0.4405, 0.3517],
    'recall':    [0.8128, 0.7686, 0.6329, 0.8088],
    'f1_score':  [0.6003, 0.5536, 0.5195, 0.4902],
    'roc_auc':   [0.8819, 0.8370, 0.8299, 0.8307],
})
model_results.to_parquet(os.path.join(DATA_DIR, 'model_results.parquet'), index=False)
print("model_results.parquet saved")

print("\n✓ Todos os datasets gerados com sucesso!")
