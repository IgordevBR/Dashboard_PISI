from dash import html, dcc


def create_pricing_layout():
    return html.Div([
        html.Div(
            '💰  Analise como preço, desconto e estratégia comercial impactam o desempenho dos jogos.',
            className='page-subtitle'
        ),

        # Row 1: Price vs Reviews scatter + Revenue by price bucket
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Preço vs. Volume de Reviews (proxy de popularidade)', className='card-title'),
                dcc.Graph(id='chart-price-vs-reviews', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Faturamento Estimado por Faixa de Preço', className='card-title'),
                dcc.Graph(id='chart-revenue-by-price-bucket', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 2: Discount analysis
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Desconto vs. Faturamento Estimado', className='card-title'),
                dcc.Graph(id='chart-discount-vs-revenue', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Distribuição de Descontos por Cluster', className='card-title'),
                dcc.Graph(id='chart-discount-by-cluster', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 3: Revenue proxy top games table + Free vs paid
        html.Div(className='chart-grid-12', children=[
            html.Div(className='card', children=[
                html.Div('Grátis vs. Pago — Sucesso Comercial', className='card-title'),
                dcc.Graph(id='chart-free-vs-paid', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Top 20 Jogos por Faturamento Estimado', className='card-title'),
                html.Div(id='table-top-revenue', style={'overflowY': 'auto', 'maxHeight': '320px'}),
            ]),
        ]),
    ])
