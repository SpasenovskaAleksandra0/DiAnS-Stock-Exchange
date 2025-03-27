import io
from datetime import datetime

import plotly.graph_objects as go
import yfinance as yf
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get form data
        ticker = request.form['ticker'].upper()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or datetime.now().strftime('%Y-%m-%d')

        # Fetch stock data
        stock = yf.Ticker(ticker)
        if not start_date:
            history = stock.history(period="6mo").reset_index()
        else:
            history = stock.history(start=start_date, end=end_date, interval='1d').reset_index()

        # Check if data is available
        if history.empty:
            return jsonify({'error': 'No data found for the selected date range.'})

        # Create subplots
        fig = go.Figure()

        # Add individual line traces for Open, High, Low, Close, and Volume
        fig.add_trace(go.Scatter(
            x=history['Date'], y=history['Open'], mode='lines', name='Open',
            line=dict(color='blue', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=history['Date'], y=history['High'], mode='lines', name='High',
            line=dict(color='green', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=history['Date'], y=history['Low'], mode='lines', name='Low',
            line=dict(color='red', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=history['Date'], y=history['Close'], mode='lines', name='Close',
            line=dict(color='orange', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=history['Date'], y=history['Volume'], mode='lines', name='Volume',
            line=dict(color='purple', width=2),
            yaxis="y2"  # Use secondary y-axis for Volume
        ))

        # Add buttons for toggling visibility of traces
        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="down",
                    buttons=[
                        dict(label="Show All",
                             method="update",
                             args=[{"visible": [True] * len(fig.data)}]),
                        dict(label="Hide All",
                             method="update",
                             args=[{"visible": [False] * len(fig.data)}]),
                        dict(label="Show Open",
                             method="update",
                             args=[{"visible": [True] + [False] * (len(fig.data) - 1)}]),
                        dict(label="Show High",
                             method="update",
                             args=[{"visible": [False, True] + [False] * (len(fig.data) - 2)}]),
                        dict(label="Show Low",
                             method="update",
                             args=[{"visible": [False] * 2 + [True] + [False] * (len(fig.data) - 3)}]),
                        dict(label="Show Close",
                             method="update",
                             args=[{"visible": [False] * 3 + [True] + [False] * (len(fig.data) - 4)}]),
                        dict(label="Show Volume",
                             method="update",
                             args=[{"visible": [False] * 4 + [True]}])
                    ]
                )
            ],
            title=f"{ticker} Stock Metrics Over Time",
            xaxis_title="Date",
            yaxis_title="Price",
            yaxis2=dict(
                title="Volume",
                overlaying="y",
                side="right"
            )
        )

        # Convert the figure to JSON
        graph_json = fig.to_json()

        # Prepare table data
        table_data = history[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
        table_data['Date'] = table_data['Date'].dt.strftime('%Y-%m-%d')
        table_data = table_data.to_dict('records')

        return jsonify({
            'chart_data': graph_json,
            'table_data': table_data,
            'ticker': ticker
        })

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/download_csv', methods=['POST'])
def download_csv():
    try:
        # Get form data
        ticker = request.form['ticker'].upper()
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date') or datetime.now().strftime('%Y-%m-%d')

        # Fetch stock data
        stock = yf.Ticker(ticker)
        if not start_date:
            history = stock.history(period="6mo").reset_index()
        else:
            history = stock.history(start=start_date, end=end_date, interval='1d').reset_index()

        # Check if data is available
        if history.empty:
            return jsonify({'error': 'No data found for the selected date range.'})

        # Prepare data for CSV
        history['Date'] = history['Date'].dt.strftime('%Y-%m-%d')
        csv_data = history[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

        # Create a BytesIO buffer to hold the CSV data
        csv_buffer = io.StringIO()
        csv_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)  # Reset buffer position

        # Send the CSV file as a response
        return send_file(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f"{ticker}_stock_data.csv"
        )

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
