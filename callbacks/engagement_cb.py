import numpy as np
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output
from utils.data_loader import load_main_data, apply_filters
from callbacks.theme import base_layout, empty_fig, ACCENT, TEXT, TEXT_MUT, CLUSTER_COLORS


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

    # ── Engagement scatter ────────────────────────────────────────────────────
    @app.callback(Output('chart-engagement-scatter', 'figure'), *FILTER_INPUTS)
    def update_engagement_scatter(tags, price_range, ratio_min, clusters,
                                  steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[(d['avg_hours'] > 0) & (d['est_revenue_proxy'] > 0)]
        if d.empty:
            return empty_fig()

        sample = d.sample(min(5000, len(d)), random_state=42)
        colors = [CLUSTER_COLORS[c] for c in sample['cluster']]

        fig = go.Figure()
        for cid, cname in {0: 'Alto Faturamento', 1: 'Boa Avaliação',
                           2: 'Alto Engajamento', 3: 'Estratégia Promocional'}.items():
            sub = sample[sample['cluster'] == cid]
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(
                x=sub['avg_hours'],
                y=sub['est_revenue_proxy'],
                mode='markers',
                name=f'Cluster {cid} — {cname}',
                marker=dict(
                    color=CLUSTER_COLORS[cid],
                    size=5,
                    opacity=0.55,
                    line=dict(width=0),
                ),
                hovertemplate=(
                    '<b>%{text}</b><br>'
                    'Horas: %{x:.1f}h<br>'
                    'Revenue proxy: $%{y:,.0f}<extra></extra>'
                ),
                text=sub['title'],
            ))

        layout = base_layout(height=400)
        layout['xaxis']['title'] = 'Média de Horas Jogadas (escala log)'
        layout['xaxis']['type'] = 'log'
        layout['yaxis']['title'] = 'Faturamento Estimado — Revenue Proxy (log)'
        layout['yaxis']['type'] = 'log'
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig

    # ── Hours by tag boxplot ───────────────────────────────────────────────────
    @app.callback(Output('chart-hours-by-tag', 'figure'), *FILTER_INPUTS)
    def update_hours_by_tag(tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[d['avg_hours'] > 0]
        if d.empty:
            return empty_fig()

        tag_counts = d['primary_tag'].value_counts().head(8).index.tolist()
        d_top = d[d['primary_tag'].isin(tag_counts)]
        fig = go.Figure()
        for i, tag in enumerate(tag_counts):
            sub = d_top[d_top['primary_tag'] == tag]['avg_hours'].clip(upper=200)
            color = f'hsl({i * 40}, 60%, 55%)'
            fig.add_trace(go.Box(
                y=sub, name=tag,
                marker_color=color,
                line_color=color,
                fillcolor=color.replace(')', ', 0.25)').replace('hsl', 'hsla'),
                boxmean=False,
                hovertemplate=f'<b>{tag}</b><br>Horas: %{{y:.1f}}<extra></extra>',
            ))

        layout = base_layout(height=320)
        layout['yaxis']['title'] = 'Horas Jogadas'
        layout['yaxis']['type'] = 'log'
        layout['showlegend'] = False
        layout['xaxis']['tickangle'] = -30
        fig.update_layout(**layout)
        return fig

    # ── Price vs hours scatter ────────────────────────────────────────────────
    @app.callback(Output('chart-price-vs-hours', 'figure'), *FILTER_INPUTS)
    def update_price_vs_hours(tags, price_range, ratio_min, clusters,
                              steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[(d['price_final'] > 0) & (d['avg_hours'] > 0)]
        if d.empty:
            return empty_fig()

        sample = d.sample(min(3000, len(d)), random_state=1)
        fig = go.Figure(go.Scatter(
            x=sample['price_final'],
            y=sample['avg_hours'],
            mode='markers',
            marker=dict(
                color=sample['positive_ratio'],
                colorscale=[[0, '#c05050'], [0.5, '#f4c842'], [1, '#a9c47f']],
                size=4, opacity=0.6,
                showscale=True,
                colorbar=dict(
                    title='Aprovação %',
                    tickfont=dict(color=TEXT_MUT, size=9),
                    titlefont=dict(color=TEXT_MUT, size=10),
                    len=0.7,
                ),
            ),
            hovertemplate='<b>%{text}</b><br>Preço: $%{x:.2f}<br>Horas: %{y:.1f}h<extra></extra>',
            text=sample['title'],
        ))

        layout = base_layout(height=320)
        layout['xaxis']['title'] = 'Preço Final (USD)'
        layout['yaxis']['title'] = 'Média de Horas Jogadas'
        layout['yaxis']['type'] = 'log'
        fig.update_layout(**layout)
        return fig

    # ── Steam Deck comparison ─────────────────────────────────────────────────
    @app.callback(Output('chart-steam-deck-compare', 'figure'), *FILTER_INPUTS)
    def update_steam_deck(tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        grp = d.groupby('steam_deck').agg(
            avg_hours_med=('avg_hours', 'median'),
            rev_med=('est_revenue_proxy', 'median'),
            pos_ratio=('positive_ratio', 'mean'),
            success_rate=('commercial_success', 'mean'),
            count=('app_id', 'count'),
        ).reset_index()
        grp['label'] = grp['steam_deck'].map({True: 'Steam Deck ✓', False: 'Sem Steam Deck'})

        metrics = [
            ('avg_hours_med', 'Horas Medianas'),
            ('pos_ratio', 'Aprovação Média (%)'),
            ('success_rate', 'Taxa de Sucesso'),
        ]

        fig = go.Figure()
        for col, name in metrics:
            fig.add_trace(go.Bar(
                x=grp['label'],
                y=grp[col],
                name=name,
                hovertemplate=f'{name}: %{{y:.2f}}<extra></extra>',
            ))

        layout = base_layout(height=320)
        layout['barmode'] = 'group'
        layout['showlegend'] = True
        layout['legend']['font'] = dict(size=10)
        fig.update_layout(**layout)
        return fig

    # ── Releases by year ──────────────────────────────────────────────────────
    @app.callback(Output('chart-releases-by-year', 'figure'), *FILTER_INPUTS)
    def update_releases_by_year(tags, price_range, ratio_min, clusters,
                                steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        yr = d.groupby('year').agg(
            total=('app_id', 'count'),
            success=('commercial_success', 'sum'),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=yr['year'], y=yr['total'],
            name='Total', marker_color='#2a475e',
            hovertemplate='Ano %{x}<br>Lançamentos: %{y:,}<extra></extra>',
        ))
        fig.add_trace(go.Bar(
            x=yr['year'], y=yr['success'],
            name='Sucesso Comercial', marker_color=ACCENT,
            hovertemplate='Ano %{x}<br>Sucessos: %{y:,}<extra></extra>',
        ))

        layout = base_layout(height=320)
        layout['barmode'] = 'overlay'
        layout['xaxis']['title'] = 'Ano'
        layout['yaxis']['title'] = 'Jogos'
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig
