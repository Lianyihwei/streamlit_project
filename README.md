# streamlit_project

pyhton 展示互動k線圖、rsi、kd、macd
使用streamlit部屬在heroku上（https://stockbystreamlit.herokuapp.com/）

在heroku上要安裝talib無法直接用requirement.txt安裝
可以參考官方網指令（https://elements.heroku.com/buildpacks/numrut/heroku-buildpack-python-talib）
同時也要將talib從requirement.txt上將talib刪除

vectorbt也有遇到python版本相容，使用python3.9.9可以順利安裝


後續預計再增加回測功能（暫時預計是rsi、macd、kd指標回測）
