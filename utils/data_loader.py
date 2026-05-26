import os
import pandas as pd
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


@lru_cache(maxsize=1)
def load_main_data() -> pd.DataFrame:
    return pd.read_parquet(os.path.join(DATA_DIR, 'steam_dashboard.parquet'))


@lru_cache(maxsize=1)
def load_cluster_profile() -> pd.DataFrame:
    return pd.read_parquet(os.path.join(DATA_DIR, 'cluster_profile.parquet'))


@lru_cache(maxsize=1)
def load_shap_data() -> pd.DataFrame:
    return pd.read_parquet(os.path.join(DATA_DIR, 'shap_importance.parquet'))


@lru_cache(maxsize=1)
def load_model_results() -> pd.DataFrame:
    return pd.read_parquet(os.path.join(DATA_DIR, 'model_results.parquet'))


def apply_filters(df: pd.DataFrame,
                  tags=None, price_range=None, positive_ratio_min=0,
                  clusters=None, steam_deck=None, year_range=None,
                  success_filter=None) -> pd.DataFrame:
    """Apply global sidebar filters to the main dataframe."""
    mask = pd.Series(True, index=df.index)

    if tags:
        tag_mask = df['tags_str'].apply(lambda x: any(t in x.split('|') for t in tags))
        mask &= tag_mask

    if price_range:
        mask &= (df['price_final'] >= price_range[0]) & (df['price_final'] <= price_range[1])

    if positive_ratio_min and positive_ratio_min > 0:
        mask &= df['positive_ratio'] >= positive_ratio_min

    if clusters is not None and len(clusters) > 0:
        mask &= df['cluster'].isin(clusters)

    if steam_deck == 'yes':
        mask &= df['steam_deck'] == True
    elif steam_deck == 'no':
        mask &= df['steam_deck'] == False

    if year_range:
        mask &= (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])

    if success_filter == 'success':
        mask &= df['commercial_success'] == 1
    elif success_filter == 'not_success':
        mask &= df['commercial_success'] == 0

    return df[mask].copy()
