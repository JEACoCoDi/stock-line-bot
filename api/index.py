from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from api.finance import Finance

# ETF, 績優股, 金融股
TYPE = "(1).股指ETF清單 \n(2).績優股清單 \n(3).金融股清單 \n(4).債券ETF清單 \n**可直接輸入您想要查詢的股票代號\n或輸入(1、2、3、4)查詢系統清單\n"\
    + "**目前買入訊號的設定條件，包括股價低於短期20日布林通道下軌線的1.05倍、RSI指標小於30、且股價小於等於買入價格（buy_price）"
ETF = {
    '0050': '元大台灣50',     
    '0056': '元大高股息',
    '006208': '富邦台灣50', 
    '00646': '元大S&P500',
    '00657': '國泰日經225',
    '00690': '兆豐藍籌30',
    '00701': '國泰股利精選30',  
    '00713': '元大台灣高息低波',
    '00757': '統一FANG+',
    '00830': '國泰費城半導體',
    '00850': '元大臺灣ESG永續',     
    '00878': '國泰永續高股息', 
    '00919': '群益台灣精選高息',
    '00923': '群益台灣ESG低碳',
    '00927': '群益半導體收益'
}
BLUE_CHIP = {
    '^TWII': '台灣加權指數',
    '^SOX': '美股費城半導體指數',
    '1102': '亞泥',    
    '2301': '光寶科',
    '2308': '台達電',
    '2317': '鴻海',
    '2324': '仁寶',
    '2330': '台積電',
    '2356': '英業達',
    '2357': '華碩',  
    '2382': '廣達',
    '2454': '聯發科', 
    '3231': '緯創',
    '3711': '日月光投控',
    '6505': '台塑'    
}
FINANCIAL = {
    '2890': '永豐金',
    '2886': '兆豐金',
    '2885': '元大金'
}
BOND_ETF = {
    '00679B': '元大美債20年',
    '00687B': '國泰20年美債',
    '00696B': '富邦美債20年',
    '00764B': '群益25年美債',
    '00768B': '復華20年美債',
    '00779B': '凱基美債25+',
    '00795B': '中信美國公債20年',
    '00857B': '永豐20年美公債',
    '00720B': '元大投資級公司債',
    '00725B': '國泰投資級公司債',
    '00740B': '富邦全球投等債'
}

# line_bot_api = LineBotApi('CnxTIV3ZENKBF4uLOFI2x2I2wwG7Y0ILmp0pR+TvHbE/pbTPpTxw3ea5qrfsfB/T4xnXZdwuBZHgFK+eXz/bE86B8Ge+YBtEt6mEduMjFf5Pi/VsNv5PrUkgK+AtTFKAKF1H05phg7v3dkKtDuSzYgdB04t89/1O/w1cDnyilFU=')
# line_handler = WebhookHandler('11ce307d39f4e16e81dc9c49c3353ca9')
line_bot_api = LineBotApi('CSwPVky+m3QO7YpXHql+EmU0ZW5CdwDQYOfM3Rn6Y16Epb7wNbkJTlsI7AqAq7t6d7+XzSPv89xy7zpsOXcG6479xeC962QeYYtKe8K7/RjbJWA34ckcfWUgUpJwhIS9CtQfZ6TpgnBSum7jfprFewdB04t89/1O/w1cDnyilFU=')
line_handler = WebhookHandler('2807960b797584f840438008437e9839')
# line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
# line_handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))
# working_status = os.getenv("DEFALUT_TALKING", default = "true").lower() == "true"

app = Flask(__name__)
finance = Finance()

# domain root
@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/webhook", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@line_handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = []
    msg = event.message.text
    if event.message.type != "text":
        return
    
    if msg == "選股" or msg== "0":
        reply = TYPE
        message.append(TextSendMessage(text = reply))
    elif msg == "ETF" or msg == "etf" or msg == "1" or msg == "1.":
        reply = "ETF: \n"
        for key, val in ETF.items():
            reply += key + " : " + val + "\n"
        message.append(TextSendMessage(text = reply))
    elif msg == "績優股" or msg == "2" or msg == "2.":
        reply = "績優股: \n"
        for key, val in BLUE_CHIP.items():
            reply += key + " : " + val + "\n"
        message.append(TextSendMessage(text = reply))
    elif msg == "金融股" or msg == "3" or msg == "3.":
        reply = "金融股: \n"
        for key, val in FINANCIAL.items():
            reply += key + " : " + val + "\n"
        message.append(TextSendMessage(text = reply))
    elif msg == "債券ETF" or msg == "4" or msg == "4.":
        reply = "債券ETF: \n"
        for key, val in BOND_ETF.items():
            reply += key + " : " + val + "\n"
        message.append(TextSendMessage(text = reply))
    elif msg in ETF or msg in BLUE_CHIP or msg in FINANCIAL or msg in BOND_ETF:
        if msg in ETF:
            reply = finance.getReplyMsg(msg + '.TW', ETF[msg])
            # img_symbol = msg
        elif msg in BLUE_CHIP:
            reply = finance.getReplyMsg(msg + '.TW', BLUE_CHIP[msg])
            # img_symbol = msg
        elif msg in FINANCIAL:
            reply = finance.getReplyMsg(msg + '.TW', FINANCIAL[msg])
            # img_symbol = msg
        elif msg in BOND_ETF:
            reply = finance.getReplyMsg(msg + '.TWO', BOND_ETF[msg])
            # img_symbol = msg
        else:
            reply = 'Sony~ Try Again~'
            message.append(TextSendMessage(text = reply))

        message.append(TextSendMessage(text = reply))
        # img_url = f"https://charles.jea.com.tw/linebot/{img_symbol}.png"
        # message.append(ImageSendMessage(
        #     original_content_url = img_url,
        #     preview_image_url = img_url
        # ))
    else:
        reply = "抱歉~輸入代號目前不在清單內喔~"
        message.append(TextSendMessage(text = reply))

    line_bot_api.reply_message(event.reply_token, message)

    return 


if __name__ == "__main__":
    app.run()