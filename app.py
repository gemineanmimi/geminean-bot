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
    "tess":     f"{BASE}/18_szm8os.jpg",
    "justin":   f"{BASE}/16_ppjrac.jpg",
    "jeness":   f"{BASE}/17_zdtqsh.jpg",
    "jamie":    f"{BASE}/15_tsuiny.jpg",
    "travis":   f"{BASE}/14_tnp7ws.jpg",
    "toby":     f"{BASE}/7_iptvxz.jpg",
    "jovita":   f"{BASE}/13_oermlh.jpg",
    "tara":     f"{BASE}/12_bttbzu.jpg",
    "thor":     f"{BASE}/10_dfxgno.jpg",
    "jocelyn":  f"{BASE}/11_zvvwon.jpg",
    "tierra":   f"{BASE}/9_eyscj8.jpg",
    "trust":    f"{BASE}/8_veum2l.jpg",
    "jasmin":   f"{BASE}/6_esm6li.jpg",
    "jasper":   f"{BASE}/2_mapmds.jpg",
    "teddy":    f"{BASE}/5_i1mw2t.jpg",
    "trio":     f"{BASE}/4_xwlzzc.jpg",
    "tylor":    f"{BASE}/3_gwqu1l.jpg",
    "thame":    f"{BASE}/1_dwrqvs.jpg",
}

# =============================================
# keyword → สำรับที่เหมาะสม
# =============================================
KEYWORD_DECKS = {
    "ความรัก":      ["tess", "jasper", "tylor", "tara", "teddy", "thame"],
    "ความสัมพันธ์": ["jasper", "tylor", "tara", "teddy", "thame", "trust", "jocelyn"],
    "การงาน":       ["justin", "jasmin", "tierra", "thor", "jamie"],
    "งาน":          ["justin", "jasmin", "tierra", "thor", "jamie"],
    "การเงิน":      ["jasmin", "jocelyn", "tierra", "trust"],
    "เงิน":         ["jasmin", "jocelyn", "tierra", "trust"],
    "ครอบครัว":     ["jocelyn", "trio", "tara"],
    "ปกป้อง":       ["tara", "thame", "trio"],
    "ตัดสินใจ":     ["tess", "justin", "thor", "tierra"],
    "พัฒนาตัวเอง":  ["tess", "jeness", "travis", "jovita"],
    "สร้างสรรค์":   ["travis", "jeness", "thor"],
    "ความเครียด":   ["jovita", "trust", "tara", "thame"],
    "เครียด":       ["jovita", "trust", "tara", "thame"],
    "ความสำเร็จ":   ["jamie", "jasmin", "tierra", "jeness"],
    "โปรเจกต์":     ["justin", "travis", "jamie", "thor"],
    "ความมั่นคง":   ["tierra", "trust", "jocelyn", "jasmin"],
    "ความกล้า":     ["thor", "jeness", "jamie"],
    "ความสงบ":      ["jovita", "tara", "trust"],
    "โชค":          ["jovita", "toby"],
}

# =============================================
# ข้อความกำลังใจ (แก้ได้ที่นี่)
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
        url = DECKS.get(name.lower())
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
                messages=[TextMessage(text="ยังไม่พบ keyword ค่ะ")]
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
    print(f"User พิมพ์: {user_text}")

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

        # catalog — รอรูปรวม (ข้อ 3)
        if user_text == "catalog":
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="🔜 catalog กำลังจะมาเร็วๆ นี้ค่ะ")]
                )
            )
            return

        # ตรวจชื่อสำรับโดยตรง เช่น พิมพ์ "tess" หรือ "Thor"
        if user_text in DECKS:
            url = DECKS[user_text]
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[ImageMessage(
                        original_content_url=url,
                        preview_image_url=url
                    )]
                )
            )
            return

        # ตรวจ keyword หัวข้อ
        for keyword, deck_names in KEYWORD_DECKS.items():
            if keyword in user_text:
                send_deck_images(event.reply_token, deck_names, line_bot_api)
                return

        # ไม่เจอ keyword เลย
        line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="ยังไม่พบ keyword ค่ะ 🙏")]
            )
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
