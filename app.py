import streamlit as st
import pandas as pd
import pandas_ta as ta
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")
st.header('STOCK DASHBOARD')
c1, c2, c3 = st.columns([5, 2, 2])
ticker_symbol = c1.text_input('請輸入股票代號(台股請加.tw)  例如 AAPL or 0050.tw . Input stock symbol like AAPL or 0050.tw', value='0050.tw')
ticker_period = c2.selectbox('下載區間', ('1y', '3y', '5y', '10y','max'), index=0)
option = c3.selectbox('展示頁面', ('基本K線與技術指標', '相關新聞', '技術指標回測結果'), 0)

@st.cache
def get_price(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period=ticker_period, interval="1d")
    df['MA20'] = ta.sma(df['Close'], 20)
    df['MA60'] = ta.sma(df['Close'], 60)
    df['MA120'] = ta.sma(df['Close'], 120)
    df['MA240'] = ta.sma(df['Close'], 240)
    macd = ta.macd(df.Close, fastperiod=12, slowperiod=26, signalperiod=9)
    df['rsi'] = ta.rsi(df.Close, timeperiod=14)
    kd = ta.stoch(high=df.High, low=df.Low, close=df.Close)
    df['k'] = kd['STOCHk_14_3_3']
    df['d'] = kd['STOCHd_14_3_3']
    df['macd'] = macd['MACD_12_26_9']
    df['macds'] = macd['MACDs_12_26_9']
    df['macdh'] = macd['MACDh_12_26_9']
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
if option == "基本K線與技術指標":
    # ohlc container
    with st.container():
        portfolio = df['Close'][-1] - df['Close'][0]
        total_return = (portfolio / df['Close'][0]) *100
        print(f'{total_return:.2f}' + '%')
        last_day_close = round(float(df["Close"][-1]), 2)
        last_day_volume = round(float(df["Volume"][-1]), 2)
        price_diff = round(float(df['Close'].diff()[-1]), 2)
        volume_diff = round(float(df['Volume'].diff()[-1]), 2)
        col1, col2, col3 = st.columns([2,2,2])
        html_str =f'''
            <h2>{ticker_symbol.upper()}</h2>
            <h3>OHLC K線圖</h3>
            <P>{ticker_period} 期間總報酬 : {total_return:.2f} %</p>
        '''

        col1.markdown(html_str, unsafe_allow_html=True)
        col2.metric(f"{date} Close 收盤價", last_day_close, price_diff)
        col3.metric(f"{date} Volume 成交量", last_day_volume, volume_diff)
        st.plotly_chart(candle_fig, use_container_width=True)

    # rsi container
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('RSI 線圖')
        col1.subheader('RSI : {}'.format(round(df['rsi'][-1], 2)))
        col2.plotly_chart(rsi_fig, use_container_width=True)

    # kd container    
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('KD 線圖')
        col1.subheader('K Value : {}'.format(round(df['k'][-1], 2)))
        col1.subheader('D Value : {}'.format(round(df['d'][-1], 2)))
        col2.plotly_chart(kd_fig, use_container_width=True)

    # mac container
    with st.container():
        col1, col2 = st.columns([2, 9])
        col1.subheader('MACD 線圖')
        col1.subheader('MACD : {}'.format(round(df['macd'][-1], 2)))
        col1.subheader('Signal : {}'.format(round(df['macds'][-1]), 2))
        col1.subheader('MacdH : {}'.format(round(df['macdh'][-1]), 2))
        col2.plotly_chart(macd_fig, use_container_width=True)

if option == "相關新聞":
    url = 'https://tw.news.search.yahoo.com/search;_ylt=AwrtXWrsM81i3DsACDxw1gt.;_ylc=X1MDMjExNDcwNTAwOARfcgMyBGZyA2ZpbmFuY2UEZnIyA3NiLXRvcARncHJpZANiNmdzOGlKMlNNLlh0S2ZxRUU0M0VBBG5fcnNsdAMwBG5fc3VnZwMxMARvcmlnaW4DdHcubmV3cy5zZWFyY2gueWFob28uY29tBHBvcwMwBHBxc3RyAwRwcXN0cmwDMARxc3RybAM0BHF1ZXJ5A0FBUEwEdF9zdG1wAzE2NTc2MTUzNDk-?p='+ticker_symbol+'&fr2=sb-top&fr=finance'
    res = requests.get(url)
    soup = BeautifulSoup(res.text)
    news = soup.select('#web h4 a')
    for new in news:
        st.subheader(new.text)
        url = new['href']
        st.write('[看新聞去](%s)' % url) 

if option == '技術指標回測結果':
    backtesting_options = st.selectbox('回測參數', ('macd', 'rsi', 'kd'), index=0)
    if backtesting_options == 'macd':
        st.markdown('### macd快線 往上突破 macd慢線 買入 . macd快線 往下跌穿 macd慢線 賣出')
        entries = df['macd'] > df['macds']
        exits = df['macd'] < df['macds']
        pf_macd = vbt.Portfolio.from_signals(df['Close'], entries, exits)
        html_str =f'''
            <h4>總交易次數 : {pf_macd.stats()[11]}     勝率 : {pf_macd.stats()[15]:.2f}</h4>
        '''
        st.markdown(html_str, unsafe_allow_html=True)
        st.plotly_chart(pf_macd.plot(), use_container_width=True)

    if backtesting_options == 'rsi':
        st.markdown('### rsi < 30 買入 . rsi > 70 賣出')
        entries = df['rsi'] < 30
        exits = df['rsi'] > 70
        pf_rsi = vbt.Portfolio.from_signals(df['Close'], entries, exits)
        html_str =f'''
            <h4>總交易次數 : {pf_rsi.stats()[11]}     勝率 : {pf_rsi.stats()[15]:.2f}%</h4>
        '''
        st.markdown(html_str, unsafe_allow_html=True)
        st.plotly_chart(pf_rsi.plot(), use_container_width=True)
    
    if backtesting_options == 'kd':
        st.markdown('### k線 往上突破 d線 買入 . k線 往下跌穿 d線 賣出')
        entries = df['k'] > df['d']
        exits = df['k'] < df['d']
        pf_kd = vbt.Portfolio.from_signals(df['Close'], entries, exits)
        html_str =f'''
            <h4>總交易次數 : {pf_kd.stats()[11]}     勝率 : {pf_kd.stats()[15]:.2f}%</h4>
        '''
        st.markdown(html_str, unsafe_allow_html=True)
        st.plotly_chart(pf_kd.plot(), use_container_width=True)