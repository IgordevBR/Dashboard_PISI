"""Shared Plotly theme and color constants for all callbacks."""

BG       = '#171a21'
BG_CARD  = '#16202d'
BG_SEC   = '#1b2838'
ACCENT   = '#66c0f4'
TEXT     = '#c6d4df'
TEXT_MUT = '#8f98a0'
GRID     = '#2a475e'
BORDER   = '#1e3144'

CLUSTER_COLORS = {
    0: '#e05c5c',
    1: '#f4b942',
    2: '#5cb85c',
    3: '#5b9bd5',
}

CLUSTER_NAMES = {
    0: 'Cluster 0 — Alto Faturamento',
    1: 'Cluster 1 — Boa Avaliação',
    2: 'Cluster 2 — Alto Engajamento',
    3: 'Cluster 3 — Estratégia Promocional',
}

RATING_COLORS = {
    'Overwhelmingly Positive': '#a9c47f',
    'Very Positive':           '#66c0f4',
    'Mostly Positive':         '#5b9bd5',
    'Positive':                '#4a8ab5',
    'Mixed':                   '#f4c842',
    'Mostly Negative':         '#e07b40',
    'Very Negative':           '#c05050',
    'Overwhelmingly Negative': '#8b2020',
}


def base_layout(title=None, height=340, margin=None):
    m = margin or dict(l=40, r=20, t=30 if title else 10, b=40)
    layout = dict(
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_CARD,
        font=dict(color=TEXT, family='Source Sans 3, sans-serif', size=12),
        height=height,
        margin=m,
        xaxis=dict(gridcolor=GRID, linecolor=BORDER, zerolinecolor=BORDER),
        yaxis=dict(gridcolor=GRID, linecolor=BORDER, zerolinecolor=BORDER),
        legend=dict(bgcolor='rgba(0,0,0,0)', bordercolor=BORDER, font=dict(size=11)),
        hoverlabel=dict(bgcolor=BG_SEC, font_color=TEXT, bordercolor=BORDER),
    )
    if title:
        layout['title'] = dict(text=title, font=dict(color=TEXT_MUT, size=12), x=0.01)
    return layout


def empty_fig(msg='Nenhum dado para os filtros selecionados.'):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(**base_layout())
    fig.add_annotation(text=msg, xref='paper', yref='paper',
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(color=TEXT_MUT, size=13))
    return fig
