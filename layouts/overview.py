from dash import html, dcc


def create_overview_layout():
    return html.Div([
        html.Div(
            '📊  Explore a distribuição geral do mercado: preços, avaliações, gêneros e correlações.',
            className='page-subtitle'
        ),

        # KPI Row
        html.Div(id='overview-kpis', className='kpi-grid'),

        # Row 1: Tag revenue + Rating distribution
        html.Div(className='chart-grid-21', children=[
            html.Div(className='card', children=[
                html.Div('Faturamento Médio por Gênero (Top Tags)', className='card-title'),
                dcc.Graph(id='chart-tag-revenue', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Distribuição por Rating', className='card-title'),
                dcc.Graph(id='chart-rating-pie', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 2: Price histogram + Positive ratio histogram
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Distribuição de Preços (USD)', className='card-title'),
                dcc.Graph(id='chart-price-dist', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Distribuição de Taxa de Aprovação', className='card-title'),
                dcc.Graph(id='chart-ratio-dist', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 3: Scatter + Heatmap
        html.Div(className='chart-grid-21', children=[
            html.Div(className='card', children=[
                html.Div('Aprovação vs. Volume de Reviews (colorido por Rating)', className='card-title'),
                dcc.Graph(id='chart-scatter-reviews', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Correlação de Spearman', className='card-title'),
                dcc.Graph(id='chart-heatmap', config={'displayModeBar': False}),
            ]),
        ]),
    ])
