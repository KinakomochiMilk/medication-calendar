import os
from datetime import datetime, timedelta
from flask import Flask, request, send_file
from flask_cors import CORS
import io

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
CORS(app)

font_path = os.path.join(os.path.dirname(__file__), 'NotoSansJP-VariableFont_wght.ttf')
pdfmetrics.registerFont(TTFont('JA-Gothic', font_path))

WEEKDAYS_JA = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"]

def draw_card(c, x, centerY, month, day, weekday_str, custom_text, times):
    c.setFont('JA-Gothic', 40)
    c.setFillColorRGB(0, 0, 0)
    
    c.drawRightString(x - 5, centerY + 30, f"{month}月")
    c.drawString(x + 2, centerY + 30, f"{day}日")
    
    c.setFont('JA-Gothic', 34)
    c.drawCentredString(x, centerY - 15, weekday_str)
    
    if custom_text:
        c.setFillColorRGB(1, 0.9, 0.9)
        c.rect(x - 65, centerY - 55, 130, 22, fill=1, stroke=0)
        
        c.setFillColorRGB(1, 0, 0)
        c.setFont('JA-Gothic', 24)
        c.drawCentredString(x, centerY - 49, custom_text)
        
    c.setFillColorRGB(1, 0, 0)
    c.setFont('JA-Gothic', 38)
    textY = centerY - 100
    
    if len(times) == 1:
        c.drawCentredString(x, textY, times[0])
    elif len(times) == 2:
        c.drawCentredString(x - 40, textY, times[0])
        c.drawCentredString(x + 40, textY, times[1])
    elif len(times) == 3:
        c.drawCentredString(x - 50, textY, times[0])
        c.drawCentredString(x, textY, times[1])
        c.drawCentredString(x + 50, textY, times[2])

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    custom_text = data.get('custom_text', '')
    times = data.get('times', ['朝', '昼', '夜'])
    
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
    
    date_list = []
    curr = start_date
    while curr <= end_date:
        date_list.append(curr)
        curr += timedelta(days=1)
        
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))
    pageW, pageH = landscape(A4)
    
    leftX = pageW / 4
    rightX = (pageW / 4) * 3
    centerY = pageH / 2
    
    for i in range(0, len(date_list), 2):
        if i > 0:
            c.showPage()
            
        d1 = date_list[i]
        w1 = WEEKDAYS_JA[int(d1.strftime('%w'))]
        draw_card(c, leftX, centerY, d1.month, d1.day, w1, custom_text, times)
        
        if i + 1 < len(date_list):
            d2 = date_list[i+1]
            w2 = WEEKDAYS_JA[int(d2.strftime('%w'))]
            draw_card(c, rightX, centerY, d2.month, d2.day, w2, custom_text, times)
            
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.setLineWidth(1)
            c.setStrokeDashArray([4, 4])
            c.line(pageW / 2, 0, pageW / 2, pageH)
            
    c.save()
    pdf_buffer.seek(0)
    
    return send_file(pdf_buffer, mimetype='application/pdf')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
