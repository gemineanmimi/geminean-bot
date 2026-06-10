import os
import random
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi,
    ReplyMessageRequest, TextMessage, ImageMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

app = Flask(__name__)

CHANNEL_SECRET = os.environ.get("CHANNEL_SECRET", "")
CHANNEL_ACCESS_TOKEN = os.environ.get("CHANNEL_TOKEN", "")

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

BASE = "https://res.cloudinary.com/dt1ynj4bd/image/upload"

# =============================================
# ข้อมูลสำรับทั้งหมด
# =============================================
DECKS = {
    "Tess":     f"{BASE}/18_szm8os.jpg",
    "Justin":   f"{BASE}/16_ppjrac.jpg",
    "Jeness":   f"{BASE}/17_zdtqsh.jpg",
    "Jamie":    f"{BASE}/15_tsuiny.jpg",
    "Travis":   f"{BASE}/14_tnp7ws.jpg",
    "Toby":     f"{BASE}/7_iptvxz.jpg",
    "Jovita":   f"{BASE}/13_oermlh.jpg",
    "Tara":     f"{BASE}/12_bttbzu.jpg",
    "Thor":     f"{BASE}/10_dfxgno.jpg",
    "Jocelyn":  f"{BASE}/11_zvvwon.jpg",
    "Tierra":   f"{BASE}/9_eyscj8.jpg",
    "Trust":    f"{BASE}/8_veum2l.jpg",
    "Jasmin":   f"{BASE}/6_esm6li.jpg",
    "Jasper":   f"{BASE}/2_mapmds.jpg",
    "Teddy":    f"{BASE}/5_i1mw2t.jpg",
    "Trio":     f"{BASE}/4_xwlzzc.jpg",
    "Tylor":    f"{BASE}/3_gwqu1l.jpg",
    "Thame":    f"{BASE}/1_dwrqvs.jpg",
}

# =============================================
# keyword → สำรับที่เหมาะสม
# =============================================
KEYWORD_DECKS = {
    "ความรัก":      ["Jasper", "Tylor", "Tara", "Teddy", "Thame", "Trust"],
    "ความสัมพันธ์": ["Jasper", "Tylor", "Tara", "Teddy", "Thame", "Trust", "Jocelyn"],
    "การงาน":       ["Justin", "Jasmin", "Tierra", "Thor", "Jamie"],
    "งาน":          ["Justin", "Jasmin", "Tierra", "Thor", "Jamie"],
    "การเงิน":      ["Jasmin", "Jocelyn", "Tierra", "Trust"],
    "เงิน":         ["Jasmin", "Jocelyn", "Tierra", "Trust"],
    "ครอบครัว":     ["Jocelyn", "Trio", "Tara"],
    "ปกป้อง":       ["Tara", "Thame", "Trio"],
    "ตัดสินใจ":     ["Tess", "Justin", "Thor", "Tierra"],
    "พัฒนาตัวเอง":  ["Tess", "Jeness", "Travis", "Jovita"],
    "สร้างสรรค์":   ["Travis", "Jeness", "Thor"],
    "ความเครียด":   ["Jovita", "Trust", "Tara", "Thame"],
    "เครียด":       ["Jovita", "Trust", "Tara", "Thame"],
    "ความสำเร็จ":   ["Jamie", "Jasmin", "Tierra", "Jeness"],
    "โปรเจกต์":     ["Justin", "Travis", "Jamie", "Thor"],
    "ความมั่นคง":   ["Tierra", "Trust", "Jocelyn", "Jasmin"],
    "ความกล้า":     ["Thor", "Jeness", "Jamie"],
    "ความสงบ":      ["Jovita", "Tara", "Trust"],
    "โชค":          ["Jovita", "Toby"],
    "ทั้งหมด":      list(DECKS.keys()),
    "สำรับทั้งหมด": list(DECKS.keys()),
}

# =============================================
# ข้อความกำลังใจ 20 ข้อ
# =============================================
ENCOURAGEMENTS = [
    "วันนี้คุณทำได้ดีมากแล้ว อย่าลืมให้รางวัลตัวเองด้วยนะ 🌸",
    "ทุกก้าวเล็กๆ ที่เดินไป คือความกล้าหาญที่ยิ่งใหญ่เสมอ ✨",
    "คุณแข็งแกร่งกว่าที่คิด และอ่อนโยนพอที่จะรู้ว่าตัวเองต้องการอะไร 💫",
    "ไม่เป็นไรถ้าวันนี้ยังไม่สมบูรณ์แบบ พรุ่งนี้มีโอกาสใหม่เสมอ 🌅",
    "จงเชื่อในกระบวนการของชีวิต ทุกอย่างกำลังเดินไปในทางที่ดี 🌿",
    "ความรู้สึกของคุณมีความหมาย อย่าดูถูกสิ่งที่หัวใจบอก 💗",
    "คุณไม่ต้องสมบูรณ์แบบ แค่เป็นตัวเองก็พอแล้ว 🦋",
    "วันที่ยากที่สุดคือวันที่สอนบทเรียนที่มีค่าที่สุด 🌙",
    "จงดูแลตัวเองด้วยความรักเหมือนที่คุณดูแลคนที่รัก 💝",
    "คุณมาถูกทางแล้ว แม้ว่าตอนนี้จะยังมองไม่เห็นปลายทาง 🌈",
    "ทุกวันที่ตื่นขึ้นมาคือของขวัญ ใช้มันอย่างมีความหมาย 🎁",
    "ความกล้าไม่ใช่การไม่กลัว แต่คือการก้าวไปแม้ว่าจะกลัว 🦁",
    "จงอดทนกับตัวเอง คุณกำลังเติบโตอยู่ในแบบที่ดีที่สุด 🌱",
    "สิ่งดีๆ กำลังรอคุณอยู่ข้างหน้า จงเดินต่อไปนะ 🌟",
    "วันนี้แค่หายใจได้ก็เก่งแล้ว บางวันมันยากพอแค่นั้น 🕊️",
    "คุณมีพลังในการเปลี่ยนแปลงสิ่งต่างๆ ได้มากกว่าที่รู้ 💪",
    "ใจดีกับตัวเองหน่อยนะ คุณพยายามมากพอแล้ว 🤍",
    "จงเชื่อในตัวเองให้มากเท่ากับที่คนที่รักคุณเชื่อ 💖",
    "ทุกประสบการณ์กำลังช่วยให้คุณเป็นคนที่ดีขึ้น 🌸",
    "วันนี้ขอให้จำไว้ว่า คุณไม่ได้อยู่คนเดียวในโลกนี้ 🌍",
]

# =============================================

def send_deck_images(reply_token, deck_names, line_bot_api):
    """ส่งรูปสำรับตามชื่อที่กำหนด (สูงสุด 5 รูปต่อครั้ง)"""
    messages = []
    for name in deck_names[:5]:
        url = DECKS.get(name)
        if url:
            messages.append(ImageMessage(
                original_content_url=url,
                preview_image_url=url
            ))
    if messages:
        line_bot_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
    else:
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text="ไม่พบสำรับที่ตรงกันค่ะ")]
            )
        )

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_text = event.message.text.strip().lower()

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)

        # กำลังใจ
        if "กำลังใจ" in user_text or user_text == "💪":
            msg = random.choice(ENCOURAGEMENTS)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=msg)]
                )
            )
            return

        # ตรวจ keyword สำรับ
        for keyword, deck_names in KEYWORD_DECKS.items():
            if keyword in user_text:
                send_deck_images(event.reply_token, deck_names, line_bot_api)
                return

        # ไม่เจอ keyword
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(
                    text="พิมพ์ keyword ได้เลยนะคะ เช่น:\n"
                         "💜 ความรัก / ความสัมพันธ์\n"
                         "💼 การงาน / โปรเจกต์\n"
                         "💰 การเงิน / ความมั่นคง\n"
                         "🏠 ครอบครัว\n"
                         "🌟 พัฒนาตัวเอง / ความสำเร็จ\n"
                         "🕊️ ความสงบ / ความเครียด\n"
                         "🃏 สำรับทั้งหมด\n"
                         "💪 กำลังใจ"
                )]
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
