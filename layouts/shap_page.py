from dash import html, dcc


def create_shap_layout():
    return html.Div([
        html.Div(
            '🧠  Interpretabilidade via SHAP (SHapley Additive exPlanations) — modelo Gradient Boosting.',
            className='page-subtitle'
        ),

        # Row 1: SHAP bar + Model comparison
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Importância das Features — SHAP (mean |SHAP value|)', className='card-title'),
                dcc.Graph(id='chart-shap-bar', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Comparação de Modelos Supervisionados', className='card-title'),
                dcc.Dropdown(
                    id='model-metric-selector',
                    options=[
                        {'label': 'ROC-AUC', 'value': 'roc_auc'},
                        {'label': 'F1-Score', 'value': 'f1_score'},
                        {'label': 'Acurácia', 'value': 'acuracia'},
                        {'label': 'Recall', 'value': 'recall'},
                        {'label': 'Precisão', 'value': 'precisao'},
                    ],
                    value='roc_auc',
                    clearable=False,
                    style={'marginBottom': '10px', 'fontSize': '12px'},
                ),
                dcc.Graph(id='chart-model-comparison', config={'displayModeBar': False}),
            ]),
        ]),

        # Row 2: SHAP dot summary (simulated) + feature insights
        html.Div(className='card', children=[
            html.Div('SHAP Summary — Impacto Individual das Features por Amostra (simulado)', className='card-title'),
            dcc.Graph(id='chart-shap-summary', config={'displayModeBar': False},
                      style={'height': '420px'}),
        ]),

        # Row 3: Feature dependence plots
        html.Div(className='chart-grid-2', children=[
            html.Div(className='card', children=[
                html.Div('Distribuição por Feature — Sucesso vs. Insucesso', className='card-title'),
                dcc.Dropdown(
                    id='shap-feature-selector',
                    options=[
                        {'label': 'Média de Horas Jogadas', 'value': 'avg_hours'},
                        {'label': 'Taxa de Aprovação (%)', 'value': 'positive_ratio'},
                        {'label': 'Desconto (%)', 'value': 'discount'},
                        {'label': 'Preço Final (USD)', 'value': 'price_final'},
                    ],
                    value='avg_hours',
                    clearable=False,
                    style={'marginBottom': '10px', 'fontSize': '12px'},
                ),
                dcc.Graph(id='chart-feature-dependence', config={'displayModeBar': False}),
            ]),
            html.Div(className='card', children=[
                html.Div('Matriz de Confusão — Gradient Boosting', className='card-title'),
                dcc.Graph(id='chart-confusion-matrix', config={'displayModeBar': False}),
            ]),
        ]),
    ])
