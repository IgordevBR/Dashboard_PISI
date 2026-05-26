import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, html
from utils.data_loader import load_main_data, apply_filters
from callbacks.theme import (base_layout, empty_fig, BG_CARD, ACCENT, TEXT,
                              TEXT_MUT, GRID, CLUSTER_COLORS, RATING_COLORS)


def register_callbacks(app):

    # ── Filter count display ───────────────────────────────────────────────────
    @app.callback(
        Output('filter-count-display', 'children'),
        Output('filter-ratio-label', 'children'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_count(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        filtered = apply_filters(df, tags, price_range, ratio_min, clusters,
                                 steam_deck, year_range, success)
        pct = len(filtered) / len(df) * 100
        return (f'{len(filtered):,} jogos ({pct:.1f}%)',
                f'≥ {ratio_min or 0}%')

    # ── KPIs ──────────────────────────────────────────────────────────────────
    @app.callback(
        Output('overview-kpis', 'children'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_kpis(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return []
        kpis = [
            ('JOGOS', f'{len(d):,}', f'{len(d)/len(df)*100:.1f}% do total'),
            ('SUCESSO COMERCIAL', f'{d["commercial_success"].sum():,}',
             f'{d["commercial_success"].mean()*100:.1f}% dos filtrados'),
            ('PREÇO MÉDIO', f'${d["price_final"].median():.2f}',
             f'mediana | máx ${d["price_final"].max():.0f}'),
            ('APROVAÇÃO MÉDIA', f'{d["positive_ratio"].mean():.1f}%',
             f'mediana {d["positive_ratio"].median():.0f}%'),
        ]
        return [html.Div(className='kpi-card', children=[
            html.Div(label, className='kpi-label'),
            html.Div(val, className='kpi-value'),
            html.Div(sub, className='kpi-sub'),
        ]) for label, val, sub in kpis]

    # ── Tag revenue bar ───────────────────────────────────────────────────────
    @app.callback(
        Output('chart-tag-revenue', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_tag_revenue(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        rows = []
        for _, row in d.iterrows():
            for tag in str(row['tags_str']).split('|')[:3]:
                rows.append({'tag': tag, 'rev': row['est_revenue_proxy']})

        import pandas as pd
        df_tags = pd.DataFrame(rows)
        top10 = df_tags['tag'].value_counts().head(10).index.tolist()
        df_tags = df_tags[df_tags['tag'].isin(top10)]
        agg = df_tags.groupby('tag')['rev'].mean().reset_index().sort_values('rev', ascending=True)

        fig = go.Figure(go.Bar(
            x=agg['rev'], y=agg['tag'],
            orientation='h',
            marker=dict(
                color=agg['rev'],
                colorscale=[[0, '#2a475e'], [1, ACCENT]],
                showscale=False,
            ),
            text=[f'${v:,.0f}' for v in agg['rev']],
            textposition='outside',
            textfont=dict(color=TEXT_MUT, size=10),
            hovertemplate='<b>%{y}</b><br>Faturamento médio: $%{x:,.0f}<extra></extra>',
        ))
        layout = base_layout(height=300)
        layout['xaxis']['title'] = 'Faturamento Estimado Médio (USD)'
        layout['yaxis']['tickfont'] = dict(size=11)
        fig.update_layout(**layout)
        return fig

    # ── Rating donut ──────────────────────────────────────────────────────────
    @app.callback(
        Output('chart-rating-pie', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_rating_pie(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        counts = d['rating'].value_counts().reset_index()
        counts.columns = ['rating', 'count']
        colors = [RATING_COLORS.get(r, '#666') for r in counts['rating']]

        fig = go.Figure(go.Pie(
            labels=counts['rating'], values=counts['count'],
            hole=0.55,
            marker=dict(colors=colors, line=dict(color='#16202d', width=2)),
            textinfo='percent',
            textfont=dict(size=10),
            hovertemplate='<b>%{label}</b><br>%{value:,} jogos (%{percent})<extra></extra>',
        ))
        layout = base_layout(height=300)
        layout['legend']['font'] = dict(size=9, color=TEXT_MUT)
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig

    # ── Price histogram ───────────────────────────────────────────────────────
    @app.callback(
        Output('chart-price-dist', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_price_dist(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        d_paid = d[d['price_final'] > 0]
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=d[d['price_final'] == 0]['price_final'],
            name='Grátis', nbinsx=1,
            marker_color='#5b9bd5', opacity=0.8,
        ))
        fig.add_trace(go.Histogram(
            x=d_paid['price_final'].clip(upper=80),
            name='Pago (≤$80)', nbinsx=40,
            marker_color=ACCENT, opacity=0.8,
        ))
        layout = base_layout(height=290)
        layout['barmode'] = 'overlay'
        layout['xaxis']['title'] = 'Preço (USD)'
        layout['yaxis']['title'] = 'Jogos'
        layout['showlegend'] = True
        fig.update_layout(**layout)
        return fig

    # ── Positive ratio histogram ──────────────────────────────────────────────
    @app.callback(
        Output('chart-ratio-dist', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_ratio_dist(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        fig = go.Figure(go.Histogram(
            x=d['positive_ratio'], nbinsx=25,
            marker=dict(
                color=d['positive_ratio'],
                colorscale=[[0, '#c05050'], [0.5, '#f4c842'], [1, '#a9c47f']],
                showscale=False,
            ),
            hovertemplate='Aprovação: %{x:.0f}%<br>Jogos: %{y:,}<extra></extra>',
        ))
        layout = base_layout(height=290)
        layout['xaxis']['title'] = 'Taxa de Aprovação (%)'
        layout['yaxis']['title'] = 'Jogos'
        fig.update_layout(**layout)
        return fig

    # ── Scatter reviews vs positive ratio ─────────────────────────────────────
    @app.callback(
        Output('chart-scatter-reviews', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_scatter_reviews(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        sample = d.sample(min(4000, len(d)), random_state=42)
        sample = sample[sample['user_reviews'] > 0]

        fig = go.Figure()
        for rating, color in RATING_COLORS.items():
            sub = sample[sample['rating'] == rating]
            if sub.empty:
                continue
            fig.add_trace(go.Scatter(
                x=sub['positive_ratio'],
                y=sub['user_reviews'],
                mode='markers',
                name=rating,
                marker=dict(color=color, size=4, opacity=0.6),
                hovertemplate='<b>%{text}</b><br>Aprovação: %{x:.0f}%<br>Reviews: %{y:,}<extra></extra>',
                text=sub['title'],
            ))

        layout = base_layout(height=340)
        layout['xaxis']['title'] = 'Taxa de Aprovação (%)'
        layout['yaxis']['title'] = 'Volume de Reviews'
        layout['yaxis']['type'] = 'log'
        layout['showlegend'] = True
        layout['legend']['font'] = dict(size=9)
        fig.update_layout(**layout)
        return fig

    # ── Spearman heatmap ──────────────────────────────────────────────────────
    @app.callback(
        Output('chart-heatmap', 'figure'),
        Input('filter-tags', 'value'),
        Input('filter-price-range', 'value'),
        Input('filter-positive-ratio', 'value'),
        Input('filter-clusters', 'value'),
        Input('filter-steam-deck', 'value'),
        Input('filter-year-range', 'value'),
        Input('filter-success', 'value'),
    )
    def update_heatmap(tags, price_range, ratio_min, clusters, steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters, steam_deck, year_range, success)
        if len(d) < 10:
            return empty_fig()

        cols = ['positive_ratio', 'user_reviews', 'price_final',
                'discount', 'est_revenue_proxy', 'avg_hours']
        labels = ['Aprovação', 'Reviews', 'Preço', 'Desconto', 'Revenue', 'Horas']
        corr = d[cols].corr(method='spearman').values

        fig = go.Figure(go.Heatmap(
            z=corr, x=labels, y=labels,
            colorscale=[[0, '#8b2020'], [0.5, '#16202d'], [1, '#4a9a6a']],
            zmin=-1, zmax=1,
            text=[[f'{v:.2f}' for v in row] for row in corr],
            texttemplate='%{text}',
            textfont=dict(size=10),
            showscale=True,
            colorbar=dict(tickfont=dict(color=TEXT_MUT, size=9)),
            hovertemplate='%{y} × %{x}: %{z:.3f}<extra></extra>',
        ))
        layout = base_layout(height=340)
        layout['xaxis']['tickfont'] = dict(size=9)
        layout['yaxis']['tickfont'] = dict(size=9)
        layout['yaxis']['autorange'] = 'reversed'
        fig.update_layout(**layout)
        return fig
