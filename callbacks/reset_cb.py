from dash import Input, Output, State


def register_callbacks(app):
    @app.callback(
        Output('filter-tags',           'value'),
        Output('filter-price-range',    'value'),
        Output('filter-positive-ratio', 'value'),
        Output('filter-clusters',       'value'),
        Output('filter-steam-deck',     'value'),
        Output('filter-year-range',     'value'),
        Output('filter-success',        'value'),
        Input('btn-reset-filters',      'n_clicks'),
        prevent_initial_call=True,
    )
    def reset_filters(n):
        return [], [0, 250], 0, [0, 1, 2, 3], 'all', [2003, 2024], 'all'
