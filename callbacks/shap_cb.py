import numpy as np
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output
from utils.data_loader import load_main_data, load_shap_data, load_model_results, apply_filters
from callbacks.theme import (base_layout, empty_fig, ACCENT, TEXT, TEXT_MUT,
                              CLUSTER_COLORS, GRID)


def register_callbacks(app):

    FILTER_INPUTS = [
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    ]

    # ── SHAP bar chart ────────────────────────────────────────────────────────
    @app.callback(Output('chart-shap-bar', 'figure'), *FILTER_INPUTS)
    def update_shap_bar(tags, price_range, ratio_min, clusters,
                        steam_deck, year_range, success):
        shap = load_shap_data()
        shap_sorted = shap.sort_values('importance', ascending=True)

        # Highlight top 3
        colors = []
        for i, imp in enumerate(shap_sorted['importance']):
            rank = len(shap_sorted) - i
            if rank == 1:
                colors.append(ACCENT)
            elif rank <= 3:
                colors.append('#4a8ab5')
            else:
                colors.append('#2a475e')

        fig = go.Figure(go.Bar(
            x=shap_sorted['importance'],
            y=shap_sorted['feature_label'],
            orientation='h',
            marker_color=colors,
            text=[f'{v:.3f}' for v in shap_sorted['importance']],
            textposition='outside',
            textfont=dict(color=TEXT_MUT, size=10),
            hovertemplate='<b>%{y}</b><br>SHAP: %{x:.3f}<extra></extra>',
        ))

        layout = base_layout(height=380)
        layout['xaxis']['title'] = 'mean(|SHAP value|)'
        layout['yaxis']['tickfont'] = dict(size=10)
        layout['showlegend'] = False
        layout['margin'] = dict(l=180, r=60, t=20, b=40)
        fig.update_layout(**layout)
        return fig

    # ── Model comparison bar ──────────────────────────────────────────────────
    @app.callback(
        Output('chart-model-comparison', 'figure'),
        Input('model-metric-selector', 'value'),
        *FILTER_INPUTS,
    )
    def update_model_comparison(metric, tags, price_range, ratio_min, clusters,
                                steam_deck, year_range, success):
        results = load_model_results()
        results_sorted = results.sort_values(metric, ascending=True)
        metric_labels = {
            'roc_auc': 'ROC-AUC',
            'f1_score': 'F1-Score',
            'acuracia': 'Acurácia',
            'recall': 'Recall',
            'precisao': 'Precisão',
        }

        highlight = results_sorted[metric].idxmax()
        colors = [
            ACCENT if i == results_sorted[metric].idxmax() else '#2a475e'
            for i in results_sorted.index
        ]

        fig = go.Figure(go.Bar(
            x=results_sorted[metric],
            y=results_sorted['modelo'],
            orientation='h',
            marker_color=[ACCENT if v == results_sorted[metric].max() else '#2a475e'
                          for v in results_sorted[metric]],
            text=[f'{v:.4f}' for v in results_sorted[metric]],
            textposition='outside',
            textfont=dict(color=TEXT_MUT, size=10),
            hovertemplate='<b>%{y}</b><br>' + metric_labels.get(metric, metric) + ': %{x:.4f}<extra></extra>',
        ))

        layout = base_layout(height=350)
        layout['xaxis']['title'] = metric_labels.get(metric, metric)
        layout['xaxis']['range'] = [0, results_sorted[metric].max() * 1.15]
        layout['yaxis']['tickfont'] = dict(size=11)
        layout['showlegend'] = False
        fig.update_layout(**layout)
        return fig

    # ── SHAP summary dot plot (simulated) ─────────────────────────────────────
    @app.callback(Output('chart-shap-summary', 'figure'), *FILTER_INPUTS)
    def update_shap_summary(tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if len(d) < 20:
            return empty_fig()

        np.random.seed(42)
        shap_meta = load_shap_data()
        features = ['avg_hours', 'positive_ratio', 'discount']
        feat_labels = ['Média de Horas Jogadas', 'Taxa de Aprovação (%)', 'Desconto (%)']
        importances = [0.95, 0.40, 0.08]

        sample = d.sample(min(500, len(d)), random_state=42)
        fig = go.Figure()

        for i, (feat, label, imp) in enumerate(zip(features, feat_labels, importances)):
            feat_vals = sample[feat].values
            feat_norm = (feat_vals - feat_vals.min()) / (feat_vals.ptp() + 1e-9)

            # SHAP value: feature correlation with success (simulated realistically)
            direction = 1 if feat != 'discount' else -0.3
            shap_vals = direction * imp * (feat_norm - 0.5) + np.random.normal(0, imp * 0.15, len(sample))

            # Jitter y
            y_jitter = i + np.random.uniform(-0.35, 0.35, len(sample))

            fig.add_trace(go.Scatter(
                x=shap_vals,
                y=y_jitter,
                mode='markers',
                name=label,
                marker=dict(
                    color=feat_norm,
                    colorscale=[[0, '#3d7fa8'], [0.5, '#888'], [1, '#e05c5c']],
                    size=4,
                    opacity=0.7,
                    showscale=(i == 0),
                    colorbar=dict(
                        title='Valor da<br>Feature',
                        tickvals=[0, 1], ticktext=['Low', 'High'],
                        tickfont=dict(color=TEXT_MUT, size=9),
                        titlefont=dict(color=TEXT_MUT, size=10),
                        len=0.5, x=1.02,
                    ) if i == 0 else None,
                ),
                hovertemplate=f'<b>{label}</b><br>SHAP: %{{x:.3f}}<extra></extra>',
            ))

        layout = base_layout(height=400)
        layout['xaxis']['title'] = 'SHAP value (impacto no output do modelo)'
        layout['xaxis']['zeroline'] = True
        layout['xaxis']['zerolinecolor'] = '#3a5a70'
        layout['yaxis']['tickvals'] = list(range(len(feat_labels)))
        layout['yaxis']['ticktext'] = feat_labels
        layout['yaxis']['tickfont'] = dict(size=11)
        layout['showlegend'] = False
        layout['margin'] = dict(l=200, r=80, t=20, b=50)
        fig.update_layout(**layout)
        return fig

    # ── Feature dependence plot ───────────────────────────────────────────────
    @app.callback(
        Output('chart-feature-dependence', 'figure'),
        Input('shap-feature-selector', 'value'),
        *FILTER_INPUTS,
    )
    def update_feature_dependence(feature, tags, price_range, ratio_min, clusters,
                                  steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        feat_labels = {
            'avg_hours':      'Média de Horas Jogadas',
            'positive_ratio': 'Taxa de Aprovação (%)',
            'discount':       'Desconto (%)',
            'price_final':    'Preço Final (USD)',
        }
        label = feat_labels.get(feature, feature)

        fig = go.Figure()
        for sval, sname, color in [(0, 'Insucesso', '#e05c5c'), (1, 'Sucesso', '#a9c47f')]:
            sub = d[d['commercial_success'] == sval]
            if sub.empty:
                continue
            vals = sub[feature].clip(upper=sub[feature].quantile(0.98))
            fig.add_trace(go.Violin(
                x=[sname] * len(vals),
                y=vals,
                name=sname,
                box_visible=True,
                meanline_visible=True,
                line_color=color,
                fillcolor=color + '33',
                opacity=0.85,
                hovertemplate=f'{label}: %{{y:.2f}}<extra></extra>',
            ))

        layout = base_layout(height=310)
        layout['yaxis']['title'] = label
        if feature in ('avg_hours', 'est_revenue_proxy'):
            layout['yaxis']['type'] = 'log'
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig

    # ── Confusion matrix heatmap ──────────────────────────────────────────────
    @app.callback(Output('chart-confusion-matrix', 'figure'), *FILTER_INPUTS)
    def update_confusion_matrix(tags, price_range, ratio_min, clusters,
                                steam_deck, year_range, success):
        # Fixed confusion matrix from the article (Gradient Boosting on test set)
        cm = np.array([[6318, 1822],
                       [381,  1654]])
        labels = ['Insucesso (0)', 'Sucesso (1)']
        total = cm.sum()

        text = [[f'{cm[i][j]:,}<br>({cm[i][j]/total*100:.1f}%)'
                 for j in range(2)] for i in range(2)]

        fig = go.Figure(go.Heatmap(
            z=cm,
            x=[f'Pred: {l}' for l in labels],
            y=[f'Real: {l}' for l in labels],
            colorscale=[[0, '#16202d'], [1, ACCENT]],
            text=text,
            texttemplate='%{text}',
            textfont=dict(size=12, color=TEXT),
            showscale=False,
            hovertemplate='Real: %{y}<br>Pred: %{x}<br>%{z:,}<extra></extra>',
        ))

        layout = base_layout(height=310)
        layout['xaxis']['tickfont'] = dict(size=11)
        layout['yaxis']['tickfont'] = dict(size=11)
        layout['yaxis']['autorange'] = 'reversed'
        layout['annotations'] = [dict(
            text=(
                f'Acurácia: 78.35% | ROC-AUC: 0.8819<br>'
                f'F1-Score (cls 1): 0.6003 | Recall: 0.8128'
            ),
            xref='paper', yref='paper',
            x=0.5, y=-0.18, showarrow=False,
            font=dict(color=TEXT_MUT, size=10),
            align='center',
        )]
        layout['margin'] = dict(l=120, r=20, t=20, b=80)
        fig.update_layout(**layout)
        return fig
