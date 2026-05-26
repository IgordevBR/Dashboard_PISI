import numpy as np
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output, html
from utils.data_loader import load_main_data, load_cluster_profile, apply_filters
from callbacks.theme import (base_layout, empty_fig, ACCENT, TEXT, TEXT_MUT,
                              CLUSTER_COLORS, CLUSTER_NAMES, GRID)


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

    # ── PCA 2D scatter ────────────────────────────────────────────────────────
    @app.callback(Output('chart-pca-scatter', 'figure'), *FILTER_INPUTS)
    def update_pca(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        sample = d.sample(min(6000, len(d)), random_state=42)
        fig = go.Figure()

        for cid in sorted(sample['cluster'].unique()):
            sub = sample[sample['cluster'] == cid]
            name = CLUSTER_NAMES.get(cid, f'Cluster {cid}')
            fig.add_trace(go.Scatter(
                x=sub['pca_x'], y=sub['pca_y'],
                mode='markers',
                name=name,
                marker=dict(
                    color=CLUSTER_COLORS[cid],
                    size=5, opacity=0.6,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    f'<b>%{{text}}</b><br>'
                    f'{name}<br>'
                    'Horas: %{customdata[0]:.1f}h | '
                    'Aprovação: %{customdata[1]:.0f}%<extra></extra>'
                ),
                text=sub['title'],
                customdata=sub[['avg_hours', 'positive_ratio']].values,
            ))

        layout = base_layout(height=440)
        layout['xaxis']['title'] = 'PC1 (35.8% variância)'
        layout['yaxis']['title'] = 'PC2 (25.9% variância)'
        layout['showlegend'] = True
        layout['legend']['font'] = dict(size=10)
        fig.update_layout(**layout)
        return fig

    # ── Cluster donut ─────────────────────────────────────────────────────────
    @app.callback(Output('chart-cluster-donut', 'figure'), *FILTER_INPUTS)
    def update_cluster_donut(tags, price_range, ratio_min, clusters,
                             steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        counts = d['cluster'].value_counts().sort_index()
        labels = [CLUSTER_NAMES.get(i, f'Cluster {i}') for i in counts.index]
        colors = [CLUSTER_COLORS[i] for i in counts.index]

        fig = go.Figure(go.Pie(
            labels=labels, values=counts.values,
            hole=0.6,
            marker=dict(colors=colors, line=dict(color='#16202d', width=2)),
            textinfo='percent',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{value:,} jogos (%{percent})<extra></extra>',
        ))
        layout = base_layout(height=180)
        layout['showlegend'] = False
        layout['margin'] = dict(l=10, r=10, t=10, b=10)
        fig.update_layout(**layout)
        return fig

    # ── Cluster profile badges ────────────────────────────────────────────────
    @app.callback(Output('cluster-profile-badges', 'children'), *FILTER_INPUTS)
    def update_cluster_badges(tags, price_range, ratio_min, clusters,
                              steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return html.Div('Sem dados', style={'color': TEXT_MUT, 'fontSize': '11px'})

        profile = d.groupby('cluster').agg(
            n=('app_id', 'count'),
            med_hours=('avg_hours', 'median'),
            med_ratio=('positive_ratio', 'median'),
            med_rev=('est_revenue_proxy', 'median'),
        ).reset_index()

        items = []
        for _, row in profile.iterrows():
            cid = int(row['cluster'])
            color = CLUSTER_COLORS[cid]
            items.append(html.Div(style={
                'borderLeft': f'3px solid {color}',
                'padding': '6px 8px',
                'marginBottom': '6px',
                'background': 'rgba(255,255,255,0.03)',
                'borderRadius': '0 4px 4px 0',
            }, children=[
                html.Div(CLUSTER_NAMES.get(cid, f'Cluster {cid}'),
                         style={'color': color, 'fontFamily': 'Rajdhani,sans-serif',
                                'fontWeight': '700', 'fontSize': '11px'}),
                html.Div(
                    f'{row["n"]:,} jogos | '
                    f'{row["med_hours"]:.1f}h med | '
                    f'{row["med_ratio"]:.0f}% ap. | '
                    f'Rev. ${row["med_rev"]:,.0f}',
                    style={'color': TEXT_MUT, 'fontSize': '10px', 'marginTop': '2px'}
                ),
            ]))
        return items

    # ── Radar chart ───────────────────────────────────────────────────────────
    @app.callback(Output('chart-cluster-radar', 'figure'), *FILTER_INPUTS)
    def update_radar(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df_full = load_cluster_profile()
        if df_full.empty:
            return empty_fig()

        profile = df_full.copy()
        if clusters:
            profile = profile[profile['cluster'].isin(clusters)]
        if profile.empty:
            return empty_fig()

        # Normalise 0-1 for radar
        metrics = ['avg_hours_median', 'positive_ratio_median',
                   'est_revenue_proxy_median', 'discount_median',
                   'commercial_success_rate']
        labels = ['Horas (med)', 'Aprovação (med)', 'Revenue (med)',
                  'Desconto (med)', 'Taxa Sucesso']

        fig = go.Figure()
        for _, row in profile.iterrows():
            cid = int(row['cluster'])
            vals = [row[m] for m in metrics]
            max_vals = [profile[m].max() + 1e-9 for m in metrics]
            norm = [v / mx for v, mx in zip(vals, max_vals)]
            norm.append(norm[0])
            theta = labels + [labels[0]]
            fig.add_trace(go.Scatterpolar(
                r=norm, theta=theta,
                fill='toself',
                name=CLUSTER_NAMES.get(cid, f'Cluster {cid}'),
                line=dict(color=CLUSTER_COLORS[cid], width=2),
                fillcolor=CLUSTER_COLORS[cid].replace('#', 'rgba(') + ',0.12)',
                marker=dict(color=CLUSTER_COLORS[cid]),
            ))

        layout = base_layout(height=320)
        layout['polar'] = dict(
            bgcolor='#16202d',
            radialaxis=dict(visible=True, range=[0, 1],
                            gridcolor=GRID, linecolor=GRID,
                            tickfont=dict(color=TEXT_MUT, size=8)),
            angularaxis=dict(gridcolor=GRID, linecolor=GRID,
                             tickfont=dict(color=TEXT_MUT, size=9)),
        )
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig

    # ── Cluster metric bars ───────────────────────────────────────────────────
    @app.callback(
        Output('chart-cluster-bars', 'figure'),
        Input('cluster-metric-selector', 'value'),
        *FILTER_INPUTS,
    )
    def update_cluster_bars(metric, tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        profile = load_cluster_profile()
        if clusters:
            profile = profile[profile['cluster'].isin(clusters)]
        if profile.empty:
            return empty_fig()

        colors = [CLUSTER_COLORS[int(c)] for c in profile['cluster']]
        vals = profile[metric]
        if metric == 'commercial_success_rate':
            vals = vals * 100

        fig = go.Figure(go.Bar(
            x=[CLUSTER_NAMES.get(int(c), f'C{c}').split('—')[1].strip()
               for c in profile['cluster']],
            y=vals,
            marker_color=colors,
            text=[f'{v:.2f}' for v in vals],
            textposition='outside',
            textfont=dict(color=TEXT_MUT, size=10),
            hovertemplate='%{x}<br>Valor: %{y:.2f}<extra></extra>',
        ))
        layout = base_layout(height=290)
        layout['showlegend'] = False
        fig.update_layout(**layout)
        return fig

    # ── Cluster success rate ──────────────────────────────────────────────────
    @app.callback(Output('chart-cluster-success-rate', 'figure'), *FILTER_INPUTS)
    def update_success_rate(tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        grp = d.groupby('cluster')['commercial_success'].agg(['sum', 'count']).reset_index()
        grp['rate'] = grp['sum'] / grp['count'] * 100

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[CLUSTER_NAMES.get(int(c), f'C{c}') for c in grp['cluster']],
            y=grp['rate'],
            marker_color=[CLUSTER_COLORS[int(c)] for c in grp['cluster']],
            text=[f'{v:.1f}%' for v in grp['rate']],
            textposition='outside',
            hovertemplate='%{x}<br>Taxa de Sucesso: %{y:.1f}%<extra></extra>',
        ))

        layout = base_layout(height=290)
        layout['yaxis']['title'] = '% com Sucesso Comercial'
        layout['showlegend'] = False
        layout['xaxis']['tickangle'] = -15
        fig.update_layout(**layout)
        return fig

    # ── Tags by cluster ───────────────────────────────────────────────────────
    @app.callback(
        Output('chart-cluster-tags', 'figure'),
        Input('cluster-tag-selector', 'value'),
        *FILTER_INPUTS,
    )
    def update_cluster_tags(sel_cluster, tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[d['cluster'] == sel_cluster]
        if d.empty:
            return empty_fig()

        rows = []
        for _, row in d.iterrows():
            for tag in str(row['tags_str']).split('|'):
                rows.append(tag)

        tag_counts = pd.Series(rows).value_counts().head(10)
        color = CLUSTER_COLORS.get(sel_cluster, ACCENT)

        fig = go.Figure(go.Bar(
            x=tag_counts.values, y=tag_counts.index,
            orientation='h',
            marker_color=color,
            hovertemplate='<b>%{y}</b><br>%{x:,} jogos<extra></extra>',
        ))
        layout = base_layout(height=290)
        layout['xaxis']['title'] = 'Jogos'
        layout['yaxis']['autorange'] = 'reversed'
        layout['showlegend'] = False
        fig.update_layout(**layout)
        return fig
