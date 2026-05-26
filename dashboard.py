"""
Playscope Dashboard — Plataforma analítica interativa do mercado Steam
======================================================================
Executar:
    python dashboard.py

Acesse em: http://127.0.0.1:8050
"""

import os
import sys

# Garante que o diretório do projeto esteja no path
sys.path.insert(0, os.path.dirname(__file__))

from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# ── Layouts ────────────────────────────────────────────────────────────────────
from layouts.sidebar    import create_sidebar
from layouts.overview   import create_overview_layout
from layouts.engagement import create_engagement_layout
from layouts.clusters   import create_clusters_layout
from layouts.pricing    import create_pricing_layout
from layouts.shap_page  import create_shap_layout

# ── Callbacks ──────────────────────────────────────────────────────────────────
from callbacks import (overview_cb, engagement_cb, cluster_cb,
                       pricing_cb, shap_cb, reset_cb)

# ─────────────────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    title='Playscope — Steam Analytics',
    update_title=None,
)
server = app.server   # expõe o Flask server (para deploy com gunicorn)

# ─────────────────────────────────────────────────────────────────────────────
#  Root layout
# ─────────────────────────────────────────────────────────────────────────────
app.layout = html.Div([

    # ── Top navbar ──────────────────────────────────────────────────────────
    html.Div(className='playscope-navbar', children=[
        html.Div(['PLAY', html.Span('SCOPE')], className='navbar-logo'),
        dcc.Tabs(
            id='main-tabs',
            value='overview',
            className='dash-tabs',
            children=[
                dcc.Tab(label='📊 Visão Geral',     value='overview'),
                dcc.Tab(label='🎮 Engajamento',     value='engagement'),
                dcc.Tab(label='🔬 Clusterização',   value='clusters'),
                dcc.Tab(label='💰 Mercado & Preços', value='pricing'),
                dcc.Tab(label='🧠 Interpretabilidade', value='shap'),
            ],
        ),
    ]),

    # ── Body: sidebar + content ──────────────────────────────────────────────
    html.Div(className='main-wrapper', children=[
        create_sidebar(),
        html.Div(id='page-content', className='content-area'),
    ]),
])


# ─────────────────────────────────────────────────────────────────────────────
#  Page routing callback
# ─────────────────────────────────────────────────────────────────────────────
@app.callback(Output('page-content', 'children'), Input('main-tabs', 'value'))
def render_page(tab):
    pages = {
        'overview':   create_overview_layout,
        'engagement': create_engagement_layout,
        'clusters':   create_clusters_layout,
        'pricing':    create_pricing_layout,
        'shap':       create_shap_layout,
    }
    return pages.get(tab, create_overview_layout)()


# ─────────────────────────────────────────────────────────────────────────────
#  Register all callbacks
# ─────────────────────────────────────────────────────────────────────────────
overview_cb.register_callbacks(app)
engagement_cb.register_callbacks(app)
cluster_cb.register_callbacks(app)
pricing_cb.register_callbacks(app)
shap_cb.register_callbacks(app)
reset_cb.register_callbacks(app)


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8050)
