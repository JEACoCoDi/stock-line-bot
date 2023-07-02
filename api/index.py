from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, ImageMessage, TextSendMessage, ImageSendMessage
from api.finance import Finance
# import os

# ETF, 績優股, 金融股
TYPE = "(1).股指ETF清單 \n(2).績優股清單 \n(3).金融股清單 \n(4).債券ETF清單 \n**可直接輸入您想要查詢的股票代號\n或輸入(1、2、3、4)查詢系統清單"
ETF = {
    '0050.TW': '元大台灣50',     
    '0056.TW': '元大高股息',
    '006208.TW': '富邦台灣50', 
    '00646.TW': '元大S&P500',
    '00657.TW': '國泰日經225',
    '00690.TW': '兆豐藍籌30',
    '00701.TW': '國泰股利精選30',  
    '00713.TW': '元大台灣高息低波',
    '00757.TW': '統一FANG+',
    '00830.TW': '國泰費城半導體',
    '00850.TW': '元大臺灣ESG永續',     
    '00878.TW': '國泰永續高股息', 
    '00919.TW': '群益台灣精選高息',
    '00927.TW': '群益半導體收益'
}
BLUE_CHIP = {
    '^TWII': '台灣加權指數',
    '^SOX': '美股費城半導體指數',
    '2356.TW': '英業達',
    '2330.TW': '台積電', 
    '2454.TW': '聯發科', 
    '2357.TW': '華碩', 
    '6505.TW': '台塑',
    '1102.TW': '亞泥',
    '2324.TW': '仁寶',
    '2308.TW': '台達電',
    '3711.TW': '日月光投控',
    '2382.TW': '廣達',
    '3231.TW': '緯創',
    '2301.TW': '光寶科'
}
FINANCIAL = {
    '2890.TW': '永豐金',
    '2886.TW': '兆豐金',
    '2885.TW': '元大金'
}
BOND_ETF = {
    '00679B.TW': '元大美債20年',
    '00687B.TW': '國泰20年美債',
    '00696B.TW': '富邦美債20年',
    '00764B.TW': '群益25年美債',
    '00768B.TW': '復華20年美債',
    '00779B.TW': '凱基美債25+',
    '00795B.TW': '中信美國公債20年',
    '00857B.TW': '永豐20年美公債',
    '00720B.TW': '元大投資級公司債',
    '00725B.TW': '國泰投資級公司債',
    '00740B.TW': '富邦全球投等債'
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
            reply = finance.getReplyMsg(msg, ETF[msg])
            #img_url = finance.getImg(msg)
        elif msg in BLUE_CHIP:
            reply = finance.getReplyMsg(msg, BLUE_CHIP[msg])
            #img_url = finance.getImg(msg)
        elif msg in FINANCIAL:
            reply = finance.getReplyMsg(msg, FINANCIAL[msg])
            #img_url = finance.getImg(msg)
        elif msg in BOND_ETF:
            reply = finance.getReplyMsg(msg, BOND_ETF[msg])
            #img_url = finance.getImg(msg)
        else:
            reply = '抱歉，請再試一次'

        message.append(TextSendMessage(text = reply))
        img_url = "https://drive.google.com/file/d/1ibZKokvRfCz_R2Wzfpa1vCFfZsArpHaj/view?usp=sharing"
        message.append(ImageSendMessage(
            original_content_url = img_url,
            preview_image_url = img_url
        ))
    else:
        reply = "我不知道你在說什麼"

    line_bot_api.reply_message(event.reply_token, message)

    return 

if __name__ == "__main__":
    app.run()
