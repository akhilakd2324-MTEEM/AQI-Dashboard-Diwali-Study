import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------
# LOAD DATA
# ---------------------------------------
df = pd.read_csv("merged_aqi.csv")

# first column is City, remaining columns are dates
date_columns = df.columns[1:]
cities = sorted(df["City"].dropna().astype(str).unique())


# ---------------------------------------
# CREATE DASH APP
# ---------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("India Air Quality Dashboard", 
            style={'textAlign': 'center'}),

    dcc.Dropdown(
        id='city-dropdown',
        options=[{"label": c, "value": c} for c in cities],
        value="Delhi",
        style={'width': '50%', 'margin': 'auto'}
    ),

    dcc.Slider(
        id='time-slider',
        step=1,
    ),

    html.Br(),
    dcc.Graph(id='gauge-chart'),
    dcc.Graph(id='trend-chart')

])


# ---------------------------------------
# SINGLE CALLBACK (NO DUPLICATE OUTPUTS)
# ---------------------------------------
@app.callback(
    Output('time-slider', 'min'),
    Output('time-slider', 'max'),
    Output('time-slider', 'marks'),
    Output('time-slider', 'value'),
    Output('gauge-chart', 'figure'),
    Output('trend-chart', 'figure'),
    Input('city-dropdown', 'value'),
    Input('time-slider', 'value')
)
def update_dashboard(city, selected_idx):

    # fix first-run case
    if selected_idx is None:
        selected_idx = 0

    # slider settings
    marks = {i: date_columns[i] for i in range(0, len(date_columns), 30)}
    min_idx = 0
    max_idx = len(date_columns) - 1
    current_date = date_columns[selected_idx]

    # get AQI value
    aqi_value = df.loc[df["City"] == city, current_date].values[0]

    # -------------------------------------------------
    # GAUGE CHART
    # -------------------------------------------------
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=aqi_value,
        title={'text': f"{city} — {current_date}"},
        gauge={
            'axis': {'range': [0, 500]},
            'steps': [
                {'range': [0, 50], 'color': 'green'},
                {'range': [51, 100], 'color': 'yellow'},
                {'range': [101, 200], 'color': 'orange'},
                {'range': [201, 300], 'color': 'red'},
                {'range': [301, 500], 'color': 'purple'},
            ],
            'bar': {'color': 'black'}
        }
    ))

    # -------------------------------------------------
    # TREND CHART
    # -------------------------------------------------
    y = df[df["City"] == city].iloc[0, 1:]

    trend_fig = go.Figure()
    trend_fig.add_scatter(
        x=date_columns,
        y=y,
        mode='lines+markers',
        name=city
    )
    trend_fig.update_layout(
        title=f"AQI Trend for {city}",
        xaxis_title="Date",
        yaxis_title="AQI"
    )

    return min_idx, max_idx, marks, selected_idx, gauge_fig, trend_fig


# ---------------------------------------
# RUN APP
# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
