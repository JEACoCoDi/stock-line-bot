import numpy as np
import pandas as pd  
import yfinance as yf
import datetime

class Finance:
    def __init__(self):
        self.symbol = {}

    def getDate(self):
        DateTime = datetime.datetime.now()
        Y1 = DateTime.year
        M1 = DateTime.month
        D1 = DateTime.day
        dateStr = str(Y1)+"/"+str(M1)+"/"+str(D1)    
        return dateStr
    
    def getData(self, symbol):                
        # 下載股價資料-最近1年
        df = yf.download(symbol, period='1y')
        
        # 計算移動平均線
        df['MA20'] = df['Close'].rolling(window=20).mean()
        #df['MA45'] = df['Close'].rolling(window=45).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        df['MA120'] = df['Close'].rolling(window=120).mean()      ###半年線

        # 從資料中提取最高價（high）和最低價（low） 
        high_values = df['High'].values 
        low_values = df['Low'].values

        # 計算 william 指數
        #使用過去20天週期的計算方式:WILLIAM指數的計算公式為：(過去20天收盤最高價-當日收盤價) / 過去20天最高價 - 過去20天最低價) * -100
        window_size = 20
        high_values = df['High'].rolling(window_size).max()
        low_values = df['Low'].rolling(window_size).min()
        df['WILLIAMS'] = ((high_values - df['Close'][-1]) / (high_values - low_values)) * 100

        # 計算 MFI 資金流向指標
        #MFI資金流向指標的計算公式為：100 - (100 / (1 + money_flow_ratio))
        adl = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / (df['High'] - df['Low']) * df['Volume']
        adl = adl.cumsum()
        df['ADL'] = adl

        # 計算 MFI
        typical_price = (df['High'] + df['Low'] + df['Close']) / 3
        money_flow = typical_price * df['Volume']
        positive_flow = np.where(typical_price > typical_price.shift(1), money_flow, 0)
        negative_flow = np.where(typical_price < typical_price.shift(1), money_flow, 0)
        positive_flow_sum = pd.Series(positive_flow).rolling(window=14).sum()
        negative_flow_sum = pd.Series(negative_flow).rolling(window=14).sum()
        money_flow_ratio = np.where(negative_flow_sum == 0, 0.5, positive_flow_sum / negative_flow_sum)
        mfi = 100 - (100 / (1 + money_flow_ratio))
        df['MFI'] = mfi

        # 計算RSI指標
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 計算20天的布林通道上下限，此部分可依照實際情況，修改成45天或90天布林通道
        df['std'] = df['Close'].rolling(window=20).std()
        df['upper'] = df['MA20'] + 2 * df['std']
        df['lower'] = df['MA20'] - 2 * df['std']

        # 利用前一個月的布林通道上下限來計算最佳買入價格和停損價格
        df['diff'] = df['upper'] - df['lower']
        df['buy_price'] = df['lower'].rolling(window=45).mean() + 0.2 * df['diff'].rolling(window=45).mean()
    
        # 這個公式的目的是要讓投資人在股價處於低點時買進，
        # 並且設定一個停損價格，以控制風險。
        # 這個公式的核心是利用布林通道的下限來判斷股價是否處於低點，
        # 再加上一個緩衝區間，以避免買進時股價已經反彈。
        # 而這個緩衝區間的大小，就是由0.2倍的布林通道上下限區間差來決定的。
        df['stop_loss_price'] = df['lower'].rolling(window=45).mean() + 0.1 * df['diff'].rolling(window=45).mean()

        # 找出最佳買入點
        df['signal'] = 0
        df.loc[(df['Close'] < df['lower'] * 1.05) & (df['RSI'] < 30) & (df['Close'] <= df['buy_price']), 'signal'] = 1
        #這段程式碼是用來判斷是否有買入訊號的條件，其中包括股價低於布林通道下軌線（lower）的1.05倍、RSI指標小於30、且股價小於等於買入價格（buy_price）。如果符合這些條件，則會在對應的資料列中標記signal為1，表示有買入訊號。
        #至於如何決定最佳買入點，這通常需要考慮多種因素，例如技術指標、基本面分析、市場趨勢等等。這些因素可以根據個人的投資策略和風險偏好進行綜合考慮，以找出最佳的買入點。建議在進行投資前，先進行充分的研究和分析，並制定出明確的投資策略和風險控制措施。

        #計算股價與季線的差距
        # price_difference = df['Close'][-1] - df['MA60']

        return df
  
    def getReplyMsg(self, symbol, name):

        df = self.getData(symbol)

        last_close = df['Close'][-1]
        last_buy_price = df['buy_price'][-1]
        last_stop_loss_price = df['stop_loss_price'][-1]
        last_rsi = df['RSI'][-1]
        #計算季均價差值
        price_difference = df['Close'][-1] - df['MA60'][-1]

        if df['signal'][-1] == 1:
            keyword = f'收盤價[{last_close:.2f}元], 已經出現買入訊號了!\n' \
                    + '**買入訊號設定條件為: 股價已低於布林通道下軌線的1.05倍、且RSI指標小於30、且股價低於估算的合理買入價格。\n' \
                    + '建議趕快買進，買入參考價格為' + str(round(last_buy_price*0.995, 2)) + '元。(祝發大財~)\n' \
                    + '另提供參考停損價格為' + str(round(last_stop_loss_price, 2)) + '元。'    
        elif last_close >= df['MA20'][-1] and last_close >= df['MA60'][-1] and last_close >= df['upper'][-1]*0.995:
            keyword = f'收盤價[{last_close:.2f}元], 已高於MA20月均線及MA60季均線且超過布林上限。\n' \
                    + '強烈建議可賣出。\n' \
                    + '賣出參考價格:' + str(round(last_close*1.005, 2)) + '元。(發大財了~)\n' \
                    + 'RSI指標為 ' + str(round(last_rsi, 2))   
        elif last_close >= df['MA20'][-1] and last_close >= df['upper'][-1]*0.995:
            keyword = f'收盤價[{last_close:.2f}元], 已高於MA20月均線且超過布林上限。\n' \
                    + '若有賣出計畫，建議可賣出。\n' \
                    + '賣出參考價格為' + str(round(last_close*1.005, 2)) + '元。\n' \
                    + 'RSI指標為 ' + str(round(last_rsi, 2)) 
        elif last_close <= df['MA20'][-1] and last_close <= df['MA60'][-1] and last_close <= df['lower'][-1]*1.005:
            keyword = f'收盤價[{last_close:.2f}元], 已低於MA20月均線及MA60季均線且低於布林下限。\n' \
                    +'強烈建議可加碼買進!!! (讓您發財~)\n' \
                    +'RSI指標為 ' + str(round(last_rsi, 2))    
        elif last_close <= df['MA20'][-1] and last_close <= df['lower'][-1]*1.005:
            keyword = f'收盤價[{last_close:.2f}元], 已低於MA20月均線且低於布林下限。\n' \
                    + '若有要加碼買進的計畫，建議可以準備了喔。 (讓您發財~)\n' \
                    + 'RSI指標為 ' + str(round(last_rsi, 2))    
        else:
            keyword = f'收盤價[{last_close:.2f}元], 還在布林通道內。\n' \
                    + '建議持續觀望~\n' \
                    + 'RSI指標為 ' + str(round(last_rsi, 2))
            
        replyMsg = self.getDate() + "\n"
        replyMsg += "【" + symbol + " " + name + "】" + "\n\n"
        replyMsg += keyword + "\n\n"
        replyMsg += "===指標參考===" + "\n"                
        replyMsg += "*最佳買點[D20]: " + str(round(last_buy_price, 2)) + "元\n"
        replyMsg += "*布林通道上限[BU20]: " + str(round(df['upper'][-1],2)) + "\n"
        replyMsg += "*月均線參考值[MA20]: " + str(round(df['MA20'][-1],2)) + "\n"
        replyMsg += "*季均線參考值[MA60]: " + str(round(df['MA60'][-1],2)) + "\n"
        replyMsg += "*布林通道下限[BL20]: " + str(round(df['lower'][-1],2)) + "\n"
        replyMsg += "*Williams[WD20]: " + str(round(df['WILLIAMS'][-1],2)) + "%\n"
        replyMsg += "*MFI資金流向指標: " + str(round(df['MFI'][-1],2)) + "\n"
        replyMsg += "*A/D Line指標: " + str(round(df['ADL'][-1]/10000,2)) + "\n\n"
        replyMsg += "===操作參考===" + "\n"
        replyMsg += "*最近一日股價: " + str(round(df['Close'][-1],2)) + "\n"
        replyMsg += "*股價與季線的差距: " + str(round(price_difference,2))  + " (" + str(round((price_difference/df['MA60'][-1])*100,2)) + "%)" + "\n"
        replyMsg += "*漲2.0%的股價: " + str(round(df['Close'][-1] * 1.020,2))  + "\n"
        replyMsg += "*漲1.5%的股價: " + str(round(df['Close'][-1] * 1.015,2))  + "\n"
        replyMsg += "*跌1.5%的股價: " + str(round(df['Close'][-1] * 0.985,2))  + "\n"
        replyMsg += "*跌2.0%的股價: " + str(round(df['Close'][-1] * 0.980,2))  + "\n"
        # replyMsg += '操作建議: \n'
        # replyMsg += keyword + "\n"

        return replyMsg
