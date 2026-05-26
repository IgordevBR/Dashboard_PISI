import numpy as np
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output, html
from utils.data_loader import load_main_data, apply_filters
from callbacks.theme import (base_layout, empty_fig, ACCENT, TEXT, TEXT_MUT,
                              CLUSTER_COLORS, CLUSTER_NAMES)


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

    # ── Price vs Reviews scatter ───────────────────────────────────────────────
    @app.callback(Output('chart-price-vs-reviews', 'figure'), *FILTER_INPUTS)
    def update_price_vs_reviews(tags, price_range, ratio_min, clusters,
                                steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[d['user_reviews'] > 0]
        if d.empty:
            return empty_fig()

        sample = d.sample(min(4000, len(d)), random_state=42)
        fig = go.Figure()

        for cid in sorted(sample['cluster'].unique()):
            sub = sample[sample['cluster'] == cid]
            fig.add_trace(go.Scatter(
                x=sub['price_final'],
                y=sub['user_reviews'],
                mode='markers',
                name=CLUSTER_NAMES.get(cid, f'Cluster {cid}'),
                marker=dict(color=CLUSTER_COLORS[cid], size=4, opacity=0.55),
                hovertemplate=(
                    '<b>%{text}</b><br>'
                    'Preço: $%{x:.2f}<br>'
                    'Reviews: %{y:,}<extra></extra>'
                ),
                text=sub['title'],
            ))

        layout = base_layout(height=320)
        layout['xaxis']['title'] = 'Preço Final (USD)'
        layout['yaxis']['title'] = 'Volume de Reviews'
        layout['yaxis']['type'] = 'log'
        layout['showlegend'] = True
        layout['legend']['font'] = dict(size=9)
        fig.update_layout(**layout)
        return fig

    # ── Revenue by price bucket ───────────────────────────────────────────────
    @app.callback(Output('chart-revenue-by-price-bucket', 'figure'), *FILTER_INPUTS)
    def update_revenue_by_price_bucket(tags, price_range, ratio_min, clusters,
                                       steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        bins   = [0, 0.01, 5, 15, 30, 60, 100, 250]
        labels = ['Grátis', '$0–5', '$5–15', '$15–30', '$30–60', '$60–100', '>$100']
        d = d.copy()
        d['price_bucket'] = pd.cut(d['price_final'], bins=bins, labels=labels, right=False)

        grp = d.groupby('price_bucket', observed=True).agg(
            median_rev=('est_revenue_proxy', 'median'),
            count=('app_id', 'count'),
            success_rate=('commercial_success', 'mean'),
        ).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=grp['price_bucket'],
            y=grp['median_rev'],
            name='Revenue Mediano',
            marker=dict(
                color=grp['median_rev'],
                colorscale=[[0, '#2a475e'], [1, ACCENT]],
                showscale=False,
            ),
            text=[f'${v:,.0f}' for v in grp['median_rev']],
            textposition='outside',
            textfont=dict(color=TEXT_MUT, size=10),
            hovertemplate=(
                '<b>%{x}</b><br>'
                'Revenue mediano: $%{y:,.0f}<br>'
                'Jogos: %{customdata[0]:,}<br>'
                'Taxa sucesso: %{customdata[1]:.1%}<extra></extra>'
            ),
            customdata=grp[['count', 'success_rate']].values,
        ))

        layout = base_layout(height=320)
        layout['xaxis']['title'] = 'Faixa de Preço'
        layout['yaxis']['title'] = 'Revenue Proxy Mediano (USD)'
        layout['showlegend'] = False
        fig.update_layout(**layout)
        return fig

    # ── Discount vs Revenue scatter ───────────────────────────────────────────
    @app.callback(Output('chart-discount-vs-revenue', 'figure'), *FILTER_INPUTS)
    def update_discount_vs_revenue(tags, price_range, ratio_min, clusters,
                                   steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        d = d[d['est_revenue_proxy'] > 0]
        if d.empty:
            return empty_fig()

        sample = d.sample(min(4000, len(d)), random_state=7)
        fig = go.Figure(go.Scatter(
            x=sample['discount'],
            y=sample['est_revenue_proxy'],
            mode='markers',
            marker=dict(
                color=sample['positive_ratio'],
                colorscale=[[0, '#c05050'], [0.5, '#f4c842'], [1, '#a9c47f']],
                size=4, opacity=0.55,
                showscale=True,
                colorbar=dict(
                    title='Aprovação %',
                    tickfont=dict(color=TEXT_MUT, size=9),
                    titlefont=dict(color=TEXT_MUT, size=10),
                    len=0.7,
                ),
            ),
            hovertemplate=(
                '<b>%{text}</b><br>'
                'Desconto: %{x:.0f}%<br>'
                'Revenue: $%{y:,.0f}<extra></extra>'
            ),
            text=sample['title'],
        ))

        layout = base_layout(height=320)
        layout['xaxis']['title'] = 'Desconto (%)'
        layout['yaxis']['title'] = 'Revenue Proxy'
        layout['yaxis']['type'] = 'log'
        fig.update_layout(**layout)
        return fig

    # ── Discount by cluster violin/box ────────────────────────────────────────
    @app.callback(Output('chart-discount-by-cluster', 'figure'), *FILTER_INPUTS)
    def update_discount_by_cluster(tags, price_range, ratio_min, clusters,
                                   steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        fig = go.Figure()
        for cid in sorted(d['cluster'].unique()):
            sub = d[d['cluster'] == cid]['discount']
            color = CLUSTER_COLORS[cid]
            fig.add_trace(go.Violin(
                y=sub,
                name=CLUSTER_NAMES.get(cid, f'C{cid}').split('—')[-1].strip(),
                box_visible=True,
                meanline_visible=True,
                line_color=color,
                fillcolor=color + '33',
                opacity=0.8,
                hovertemplate='Desconto: %{y:.0f}%<extra></extra>',
            ))

        layout = base_layout(height=320)
        layout['yaxis']['title'] = 'Desconto (%)'
        layout['showlegend'] = False
        fig.update_layout(**layout)
        return fig

    # ── Free vs Paid success ──────────────────────────────────────────────────
    @app.callback(Output('chart-free-vs-paid', 'figure'), *FILTER_INPUTS)
    def update_free_vs_paid(tags, price_range, ratio_min, clusters,
                            steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return empty_fig()

        d = d.copy()
        d['price_type'] = d['price_final'].apply(lambda p: 'Grátis' if p == 0 else 'Pago')

        grp = d.groupby('price_type').agg(
            count=('app_id', 'count'),
            success_rate=('commercial_success', 'mean'),
            median_hours=('avg_hours', 'median'),
            median_ratio=('positive_ratio', 'median'),
            median_rev=('est_revenue_proxy', 'median'),
        ).reset_index()

        metrics = [
            ('success_rate', 'Taxa de Sucesso'),
            ('median_hours', 'Horas Medianas'),
            ('median_ratio', 'Aprovação Mediana (%)'),
        ]
        colors = ['#5b9bd5', ACCENT]

        fig = go.Figure()
        for i, (col, label) in enumerate(metrics):
            vals = grp[col]
            if col == 'success_rate':
                vals = vals * 100
            fig.add_trace(go.Bar(
                x=grp['price_type'],
                y=vals,
                name=label,
                hovertemplate=f'{label}: %{{y:.2f}}<extra></extra>',
            ))

        layout = base_layout(height=290)
        layout['barmode'] = 'group'
        layout['showlegend'] = True
        layout['legend']['font'] = dict(size=10)
        fig.update_layout(**layout)
        return fig

    # ── Top 20 revenue table ──────────────────────────────────────────────────
    @app.callback(Output('table-top-revenue', 'children'), *FILTER_INPUTS)
    def update_top_revenue_table(tags, price_range, ratio_min, clusters,
                                 steam_deck, year_range, success):
        df = load_main_data()
        d = apply_filters(df, tags, price_range, ratio_min, clusters,
                          steam_deck, year_range, success)
        if d.empty:
            return html.Div('Sem dados', style={'color': TEXT_MUT, 'fontSize': '12px'})

        top = d.nlargest(20, 'est_revenue_proxy')[
            ['title', 'price_final', 'positive_ratio',
             'user_reviews', 'est_revenue_proxy', 'cluster']
        ].reset_index(drop=True)

        header_style = {
            'background': '#1e3144',
            'color': ACCENT,
            'fontFamily': 'Rajdhani, sans-serif',
            'fontWeight': '700',
            'fontSize': '10px',
            'letterSpacing': '0.8px',
            'textTransform': 'uppercase',
            'padding': '6px 8px',
            'textAlign': 'left',
        }
        cell_style = {
            'padding': '5px 8px',
            'fontSize': '11px',
            'color': TEXT,
            'borderBottom': '1px solid #1e3144',
        }

        rows = [html.Tr([
            html.Th('Jogo', style=header_style),
            html.Th('Preço', style=header_style),
            html.Th('Aprov.', style=header_style),
            html.Th('Reviews', style=header_style),
            html.Th('Revenue', style=header_style),
            html.Th('Cluster', style=header_style),
        ])]

        for _, row in top.iterrows():
            cid = int(row['cluster'])
            ccolor = CLUSTER_COLORS[cid]
            rows.append(html.Tr([
                html.Td(row['title'][:30], style=cell_style),
                html.Td(f"${row['price_final']:.2f}", style=cell_style),
                html.Td(f"{row['positive_ratio']:.0f}%", style=cell_style),
                html.Td(f"{int(row['user_reviews']):,}", style=cell_style),
                html.Td(f"${row['est_revenue_proxy']:,.0f}", style=cell_style),
                html.Td(
                    html.Span(f'C{cid}', style={
                        'color': ccolor,
                        'fontFamily': 'Rajdhani,sans-serif',
                        'fontWeight': '700',
                        'fontSize': '11px',
                    }),
                    style=cell_style,
                ),
            ]))

        return html.Table(rows, style={
            'width': '100%',
            'borderCollapse': 'collapse',
            'fontSize': '11px',
        })
