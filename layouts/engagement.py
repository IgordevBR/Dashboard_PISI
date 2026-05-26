from dash import html, dcc


def create_engagement_layout():
    return html.Div([
        html.Div(
            '🎮  Explore como o engajamento (horas jogadas), preço e compatibilidade se relacionam com o sucesso.',
            className='page-subtitle'
        ),

        # Row 1: Main scatter (hours vs revenue)
        html.Div(className='card', children=[
            html.Div('Engajamento (Horas) vs. Faturamento Estimado — Distribuição de Densidade', className='card-title'),
            dcc.Graph(id='chart-engagement-scatter', config={'displayModeBar': False},
                      style={'height': '420px'}),
        ]),

        # Row 2: Boxplot by tag + Price vs hours
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Engajamento por Gênero / Tag', className='card-title'),
                dcc.Graph(id='chart-hours-by-tag', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Preço vs. Média de Horas Jogadas', className='card-title'),
                dcc.Graph(id='chart-price-vs-hours', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 3: Steam Deck comparison + Revenue by year
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Steam Deck: Comparativo de Performance', className='card-title'),
                dcc.Graph(id='chart-steam-deck-compare', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Jogos Lançados por Ano', className='card-title'),
                dcc.Graph(id='chart-releases-by-year', config={'displayModeBar': False}),
            ]),
        ]),
    ])
