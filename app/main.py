import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

# Load your dataset
df = pd.read_excel('data/crypto_tweets.xlsx')

# Transform 'Elon_tweet' column to binary
df['Elon_tweet'] = df['Elon_tweet'].map({'Yes': 1, 'No': 0})

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create layout
app.layout = html.Div([
    dbc.ButtonGroup([
        dbc.Button('Bitcoin', id='btc-button', color='primary', n_clicks=1),
        dbc.Button('Ethereum', id='eth-button', color='secondary'),
        dbc.Button('Dogecoin', id='doge-button', color='success'),
    ]),
    html.H1(id='currency-title'),
    dcc.Graph(id='graph'),
    html.Div(
        dcc.DatePickerRange(
            id='date-range-container',
            min_date_allowed=df['Date'].min().date(),
            max_date_allowed=df['Date'].max().date(),
            start_date=df['Date'].min().date(),
            end_date=df['Date'].max().date(),
            className='date-range-container'
        ),
        className='date-picker'
    ),
    html.Div(id='price-card', className='price-card'),
])

@app.callback(
    [Output('currency-title', 'children'),
     Output('graph', 'figure'),
     Output('price-card', 'children')],
    [Input('btc-button', 'n_clicks'),
     Input('eth-button', 'n_clicks'),
     Input('doge-button', 'n_clicks'),
     Input('date-range-container', 'start_date'),
     Input('date-range-container', 'end_date'),
     Input('graph', 'figure')]
)
def update_graph(n_btc, n_eth, n_doge, start_date, end_date, figure):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else 'btc-button'
    price = ''
    title = ''

    if button_id == 'btc-button' and n_btc is not None:
        price = 'BTC_price'
        title = 'Bitcoin'
    elif button_id == 'eth-button' and n_eth is not None:
        price = 'ETH_price'
        title = 'Ethereum'
    elif button_id == 'doge-button' and n_doge is not None:
        price = 'DOGE_price'
        title = 'Dogecoin'
    else:
        return title, figure, None

    if start_date is None or end_date is None:
        # Set a default date range if not selected
        start_date = df['Date'].min().date()
        end_date = df['Date'].max().date()

    # Filter data based on selected dates
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if figure is None:
        fig = go.Figure()
    else:
        fig = go.Figure(figure)

    # Clear existing traces
    fig.data = []

    # Add trace for price line based on current currency
    fig.add_trace(
        go.Scatter(
            x=filtered_df['Date'],
            y=filtered_df[price],
            mode='lines',
            name='Price',
            line=dict(color='blue'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y}'
        )
    )

    # Add trace for Elon tweeted points
    fig.add_trace(
        go.Scatter(
            x=filtered_df[filtered_df['Elon_tweet'] == 1]['Date'],
            y=filtered_df[filtered_df['Elon_tweet'] == 1][price],
            mode='markers',
            name='Elon tweeted',
            marker=dict(color='green', size=8),
            hovertemplate='<b>Date:</b> %{x}<br><b>Tweet:</b> %{text}<br><b>Price:</b> %{y}',
            text=filtered_df[filtered_df['Elon_tweet'] == 1]['Tweet']
        )
    )

    # Add trace for Elon didn't tweet points
    fig.add_trace(
        go.Scatter(
            x=filtered_df[filtered_df['Elon_tweet'] == 0]['Date'],
            y=filtered_df[filtered_df['Elon_tweet'] == 0][price],
            mode='markers',
            name="Elon didn't tweet",
            marker=dict(color='red', size=8),
            hovertemplate='<b>Date:</b> %{x}<br><b>Price:</b> %{y}'
        )
    )

    fig.update_layout(hovermode='closest')

    # Calculate price change percentage
    start_price = filtered_df.iloc[0][price]
    end_price = filtered_df.iloc[-1][price]
    price_change_percentage = ((end_price - start_price) / start_price) * 100

    # Format the price change percentage based on its sign
    if price_change_percentage > 0:
        price_change_percentage_formatted = html.Span(
            '{:.2f}%'.format(price_change_percentage),
            style={'color': 'green'}
        )
    elif price_change_percentage < 0:
        price_change_percentage_formatted = html.Span(
            '{:.2f}%'.format(price_change_percentage),
            style={'color': 'red'}
        )
    else:
        price_change_percentage_formatted = '{:.2f}%'.format(price_change_percentage)

    price_card = html.Div([
        html.H4('Price Card'),
        dbc.Table(
            [
                html.Tr([html.Td('Start Price'), html.Td('${:.2f}'.format(start_price))]),
                html.Tr([html.Td('End Price'), html.Td('${:.2f}'.format(end_price))]),
                html.Tr([html.Td('Price Change (%)'), html.Td(price_change_percentage_formatted)]),
            ],
            striped=True, bordered=True, hover=True
        )
    ])

    return html.H2(title + " Fluctuation (Based on Elon Musk's Tweets)", className='currency-title'), fig, price_card

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
