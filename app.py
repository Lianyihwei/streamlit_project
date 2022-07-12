import streamlit as st
import pandas as pd
import talib
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf

st.set_page_config(layout="wide")
ticker_symbol = st.text_input('Input stock symbol like AAPL or 0050.tw', value='0050.tw')
option = st.selectbox("Which Dashboard", ("Stock Chart", "More Information"), 0)

@st.cache
def get_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="10y", interval="1d")
    df['MA20'] = talib.SMA(df['Close'], 20)
    df['MA60'] = talib.SMA(df['Close'], 60)
    df['MA120'] = talib.SMA(df['Close'], 120)
    df['MA240'] = talib.SMA(df['Close'], 240)
    macd, macds, macdh = talib.MACD(df.Close, fastperiod=12, slowperiod=26, signalperiod=9)
    df['rsi'] = talib.RSI(df.Close, timeperiod=14)
    slowk, slowd = talib.STOCH(high=df.High, low=df.Low, close=df.Close)
    df['k'] = slowk
    df['d'] = slowd
    df['macd'] = macd
    df['macds'] = macds
    df['macdh'] = macdh
    return df

df = get_price(ticker_symbol)
date = df.index[-1].strftime('%Y-%m-%d')

def get_candlestick(df):
    fig = make_subplots(rows=2,
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        subplot_titles=('OHLC_K線圖', 'Volume_成交量'),
                        row_width=(0.2, 0.7))
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"],  high=df["High"], low=df['Low'], close=df['Close'],  name='OHLC K線圖', line=dict(width=1), 
                increasing_line_color='red',
                decreasing_line_color='green',
                increasing_fillcolor='red',
                decreasing_fillcolor='green'
                ), row=1, col=1
            )
    fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], line=dict(color='blue', width=1), name='MA20'
        ), row=1, col=1
        )
    fig.add_trace(go.Scatter(x=df.index, y=df['MA60'], line=dict(color='darkgoldenrod', width=1), name='MA60'), row=1, col=1
        )
    fig.add_trace(go.Scatter(x=df.index, y=df['MA120'], line=dict(color='pink', width=1), name='MA120'), row=1, col=1
        )
    fig.add_trace(go.Scatter(x=df.index, y=df['MA240'], line=dict(color='purple', width=1), name='MA240'), row=1, col=1
        )
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], showlegend=False, marker_color='red'), row=2, col=1
        )
    fig.update_layout(height=600, margin=dict(l=20, r=20, b=20, t=20),
        xaxis=dict(rangeselector=dict(buttons=list([
            dict(count=1, label="1M", step="month", stepmode="todate"),
            dict(count=3, label="3M", step="month", stepmode="backward"),
            dict(count=6, label="6M", step="month", stepmode="backward"),
            dict(count=1, label="1y", step="year", stepmode="backward"),
            dict(count=3, label="3y", step="year", stepmode="backward"),
            dict(label="All", step="all")
            ])
            ),rangeslider=dict(visible=True), type="date")
        )
    fig.update_xaxes(rangeslider_visible=False, rangebreaks=[dict(bounds=["sat", "mon"])]
        )
    return fig


def get_rsi_graph(df):
    rsi = go.Scatter(x=df.index, y=df['rsi'], line=dict(width=1), name='RSI')
    fig_rsi = go.Figure(rsi, layout=go.Layout(height=250, 
        margin=dict(l=20, r=20, b=20, t=20), xaxis_rangebreaks = [dict(bounds = ["sat", "mon"])]
        ))
    fig_rsi.add_hline(y=70, line_width=1, line_color="red",
        annotation_text="RSI-70", annotation_position="top right",  annotation_font_color="black"
        )
    fig_rsi.add_hline(y=30, line_width=1, line_color="blue",
        annotation_text="RSI-30", annotation_position="bottom right", annotation_font_color="black"
        )
    return fig_rsi

def get_kd_graph(df):
    kline = go.Scatter(x=df.index, y=df['k'], line=dict(width=1), name='K-Line')
    dline = go.Scatter(x=df.index, y=df['d'], line=dict(width=1), name='D-Line')
    data = ([kline, dline])
    fig_kd = go.Figure(data=data, layout=go.Layout(height=250, 
        margin=dict(l=20, r=20, b=20, t=20), xaxis_rangebreaks = [dict(bounds = ["sat", "mon"])]
        ))
    return fig_kd
    
def get_macd_graph(df):
    macd = go.Scatter(x=df.index, y=df['macd'], line=dict(width=1), name="MACD")
    macds = go.Scatter(x=df.index, y=df['macds'], line=dict(width=1),name="Signal")
    macdh_color = ['red' if h > 0 else 'green' for h in df['macdh']]
    macdh = go.Bar(x=df.index, y=df['macdh'], name='MacdH', marker_color=macdh_color)
    data = ([macd, macds, macdh])
    fig_macd = go.Figure(data=data, layout=go.Layout(height=250, 
        margin=dict(l=20, r=20, b=20, t=20), xaxis_rangebreaks = [dict(bounds = ["sat", "mon"])]
        ))
    return fig_macd
candle_fig = get_candlestick(df)
macd_fig = get_macd_graph(df)
rsi_fig = get_rsi_graph(df)
kd_fig = get_kd_graph(df)

st.header(option)

# option stock chart page
if option == "Stock Chart":
    # ohlc container
    with st.container():
        last_day_close = round(float(df["Close"][-1]), 2)
        last_day_volume = round(float(df["Volume"][-1]), 2)
        price_diff = round(float(df['Close'].diff()[-1]), 2)
        volume_diff = round(float(df['Volume'].diff()[-1]), 2)
        col1, col2, col3 = st.columns([2,2,2])
        # col1.subheader(f"{ticker_symbol.upper()}  Candlestick Chart K線圖")
        html_str =f'''
            <h2>{ticker_symbol.upper()}</h2>
            <h3>OHLC K線圖</h3>
        '''
        col1.markdown(html_str, unsafe_allow_html=True)
        col2.metric(f"{date} Close 收盤價", last_day_close, price_diff)
        col3.metric(f"{date} Volume 成交量", last_day_volume, volume_diff)
        st.plotly_chart(candle_fig, use_container_width=True)

    # rsi container
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('RSI CHART 14')
        col1.text('RSI : {}'.format(round(df['rsi'][-1], 2)))
        col2.plotly_chart(rsi_fig, use_container_width=True)

    # kd container    
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('KD CHART 9')
        col1.text('K Value : {}'.format(round(df['k'][-1], 2)))
        col1.text('D Value : {}'.format(round(df['d'][-1], 2)))
        col2.plotly_chart(kd_fig, use_container_width=True)

    # mac container
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('MACD CHART 12-26-9')
        col1.text('MACD : {}'.format(round(df['macd'][-1], 2)))
        col1.text('Signal : {}'.format(round(df['macds'][-1]), 2))
        col1.text('MacdH : {}'.format(round(df['macdh'][-1]), 2))
        col2.plotly_chart(macd_fig, use_container_width=True)

        
if option == "More Information":
    st.subheader("More Information")
