from fpdf import FPDF
import os
from datetime import datetime
import locale
import io
import random

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Set larger margins (left, top, right) in mm
        self.set_margins(20, 10, 20)  # Increased from default 10mm to 20mm for left and right
        # Add Unicode font
        self.add_font('DejaVu', '', 'assets/DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'assets/DejaVuSansCondensed-Bold.ttf', uni=True)
        self.add_font('DejaVu', 'I', 'assets/DejaVuSansCondensed-Oblique.ttf', uni=True)

    def header(self):
        # Add logo
        if os.path.exists('assets/logos_black.png'):
            self.image('assets/logos_black.png', 20, 8, 50)  # Adjusted x position from 10 to 20
        
        # Add contact information
        self.set_font('DejaVu', '', 10)
        self.set_text_color(0, 136, 204)  # Gray color
        
        # Calculate width of text components for right alignment
        info_text = 'info@linkdata.uz | '
        url_text = 'www.linkdata.uz'
        info_width = self.get_string_width(info_text)
        url_width = self.get_string_width(url_text)
        total_width = info_width + url_width
        
        # Position for right alignment with new margin
        x_position = self.w - total_width - 20  # Adjusted from 10 to 20
        
        # Print email part
        self.set_x(x_position)
        self.cell(info_width, 8, info_text, 0, 0)
        
        # Print URL as link
        self.set_text_color(0, 136, 204)  # Blue color for link
        self.cell(url_width, 8, url_text, 0, 0, link='http://www.linkdata.uz')
        self.ln(20)
        
        # Add horizontal line
        self.set_draw_color(0, 48, 73) # Blue color for line
        self.set_line_width(0.5)  # Make line thicker
        self.line(20, 28, self.w - 20, 28)  # Adjusted x positions from 10 to 20

    def footer(self):
        # Set position at 1.5 cm from bottom
        self.set_y(-15)
        # DejaVu italic 8
        self.set_font('DejaVu', 'I', 8)
        # Text color in gray
        self.set_text_color(128)
        # Page number
        self.cell(0, 10, f'Sahifa {self.page_no()}', 0, 0, 'C')

def format_price(price_str):
    try:
        # Remove $ and commas, then convert to float
        price = float(str(price_str).replace('$', '').replace(',', ''))
        # Format with spaces instead of commas
        return f"{price:,.0f}".replace(',', ' ')
    except (ValueError, AttributeError):
        return price_str

def create_report_auto(property_details, predicted_price, price_range):
    # Create PDF object
    pdf = ReportPDF()
    
    # First page
    pdf.add_page()
    
    # Main title with dark blue color
    pdf.set_font('DejaVu', 'B', 24)
    pdf.set_text_color(0, 48, 73)  # Dark blue color
    pdf.cell(0, 10, "Avtomobilning tavsiyaviy bozor narxi", 0, 1, 'C')
    pdf.ln(5)
    
    # Price with blue color
    pdf.set_font('DejaVu', 'B', 36)
    pdf.set_text_color(0, 136, 204)  # Blue color
    formatted_price = format_price(predicted_price)
    pdf.cell(0, 15, f"{formatted_price} AQSH Dollari", 0, 1, 'C')
    pdf.ln(5)
    
    # Subtitle
    pdf.set_font('DejaVu', 'B', 14)
    pdf.set_text_color(0, 48, 73)  # Dark gray
    pdf.cell(0, 10, "Link Auto onlayn avtomatik baholash platformasi orqali", 0, 1, 'C')
    pdf.cell(0, 10, "hisoblangan avtomobilning bozor narxi.", 0, 1, 'C')
    pdf.ln(10)
    
    # Generate random ID and add report details
    report_id = ''.join([str(random.randint(0, 9)) for _ in range(11)])
    pdf.set_font('DejaVu', '', 12)
    
    # Label color (dark gray)
    pdf.set_text_color(0, 48, 73)
    pdf.cell(10, 8, "ID: ", 0, 0, 'L')
    # Value color (blue)
    pdf.set_text_color(0, 136, 204)
    pdf.cell(0, 8, f"{report_id}", 0, 1, 'L')
    
    # Label color (dark gray)
    pdf.set_text_color(0, 48, 73)
    pdf.cell(83, 8, "Platformadan foydalanilgan sana va vaqt: ", 0, 0, 'L')
    # Value color (blue)
    pdf.set_text_color(0, 136, 204)
    pdf.cell(0, 8, f"{datetime.now().strftime('%d.%m.%Y %H:%M')}", 0, 1, 'L')
    
    # Label color (dark gray)
    pdf.set_text_color(0, 48, 73)
    pdf.cell(32, 8, "Foydalanuvchi: ", 0, 0, 'L')
    # Value color (blue)
    pdf.set_text_color(0, 136, 204)
    pdf.cell(0, 8, "Sherzod Toshpo‘latov", 0, 1, 'L')
    
    pdf.ln(15)
    
    # Property details with improved styling
    pdf.set_font('DejaVu', 'B', 16)
    pdf.set_text_color(0, 48, 73)  # Dark blue
    pdf.cell(0, 10, "Ko'chmas mulk ma'lumotlari:", 0, 1, 'L')
    pdf.ln(5)
    
    # Property details in single column with page break support
    pdf.set_font('DejaVu', '', 11)
    pdf.set_text_color(51, 51, 51)  # Dark gray
    
    # Calculate available height on current page
    available_height = pdf.h - pdf.get_y() - pdf.b_margin
    line_height = 8
    
    # Single column layout with page break support
    for key, value in property_details.items():
        if value:
            # Check if we need a new page
            if pdf.get_y() + 2 * line_height > pdf.h - pdf.b_margin:
                pdf.add_page()
                pdf.set_font('DejaVu', 'B', 16)
                pdf.set_text_color(0, 48, 73)
                pdf.cell(0, 10, "Ko'chmas mulk ma'lumotlari (davomi):", 0, 1, 'L')
                pdf.ln(5)
                pdf.set_font('DejaVu', '', 11)
                pdf.set_text_color(51, 51, 51)
            
            # Save starting position
            start_x = pdf.get_x()
            start_y = pdf.get_y()
            
            # Print the key-value pair
            pdf.set_font('DejaVu', 'B', 11)
            key_width = 70
            pdf.cell(key_width, line_height, f"{key}:", 0, 0)
            
            # Print the value
            pdf.set_font('DejaVu', '', 11)
            value_width = pdf.w - key_width - pdf.r_margin - pdf.l_margin
            pdf.multi_cell(value_width, line_height, str(value))
            
            # Move to next line if needed
            next_y = max(pdf.get_y(), start_y + line_height)
            pdf.set_xy(start_x, next_y)
    
    pdf.ln(10)  # Add some space after the details

    # Second page
    pdf.add_page()
    
    # Methodology section with improved styling
    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(0, 48, 73)  # Dark blue
    pdf.cell(0, 10, 'Hisoblash metodologiyasi', 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font('DejaVu', '', 11)
    pdf.set_text_color(51, 51, 51)  # Dark gray
    methodology_text1 = "Mashinali o'qitish asosida ishlaydigan ko'chmas mulk baholash modeli ko'chmas mulk bozoridagi tarixiy ma'lumotlardan foydalanadi. Qisqacha tushuntirilganda modelning ishlash jarayoni quyidagicha:"
    pdf.ln(5)

    # Write first part of methodology text
    pdf.multi_cell(0, 8, methodology_text1)
    pdf.ln(5)

    # Add report image with adjusted position and size
    if os.path.exists('assets/report_pic.png'):
        # Calculate center position
        image_width = 170
        x = (pdf.w - image_width) / 2
        pdf.image('assets/report_pic.png', x=x, y=pdf.get_y(), w=image_width)
        pdf.ln(80)  # Add space after image for next content

    # Write second part with bullet points
    methodology_text2 = """1. Ma'lumotlar yig'ish: Model o'tgan yillarda sotilgan ko'chmas mulklarning o'lchami, joylashuvi, holati kabi 20 dan ortiq xususiyatlarini va ularning narxlarini ochiq platformalardan oladi.
2. Ma'lumotlarni tayyorlash: Ma'lumotlar tozalanadi, ya'ni xatoligi bo'lgan yoki yetishmayotgan qiymatlar to'g'irlanadi. Keyinchalik ba'zi xususiyatlardan qo'shimcha ko'rsatkichlar yaratiladi.
3. Modelni o'qitish: Mashinali o'qitish modeli ushbu ma'lumotlar asosida tayyorlanadi.
4. Baholash: Model tayyorlanganidan so'ng, yangi mulklar haqida ma'lumot kiritiladi va model ushbu mulklarning tavsiyaviy bozor qiymatini hisoblaydi."""
    
    pdf.multi_cell(0, 8, methodology_text2)
    pdf.ln(10)
    
    # Additional information with improved styling
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(0, 48, 73)  # Dark blue
    pdf.cell(0, 10, "Ilova: Ko'rsatkichlar tasnifi", 0, 1, 'L')
    
    pdf.set_font('DejaVu', '', 11)
    pdf.set_text_color(51, 51, 51)  # Dark gray
    additional_info = """
• Hudud – avtomobil sotuvga qo'yilgan geografik joy (viloyat/shahar);
• Brend – avtomobil ishlab chiqaruvchisi nomi (Chevrolet, Toyota, Hyundai va boshqalar);
• Model nomi – avtomobil modeli yoki to'liq nomi (misol: Cobalt, Spark va boshqalar);
• Ishlab chiqarilgan yili – avtomobil ishlab chiqarilgan yil;
• Motor hajmi – Dvigatel hajmi litrlarda (masalan: 1.5, 2.0);
• Fuel (Yoqilg'i turi) – avtomobil ishlatadigan yoqilg'i turi;
• Egalik  – avtomobil kim tomonidan sotuvga qo'yilganligi;
• Kuzov turi – avtomobilning tashqi tuzilmasi;
• Rangi – avtomobilning tashqi ko'rinish rangi (oq, qora, kulrang, ko'k, qizil va h.k.);
• Holati – avtomobilning texnik va tashqi holati;
• Qo'shimcha narsalar – avtomobilda mavjud qo'shimcha qulayliklar;
• Egalar soni – avtomobilning oldingi egalarining umumiy sonini bildiradi. Eng kamida 1 raqami egasi kiritilishi kerak. Sababi, hatto yangi, ishlatilmagan avtomobil bo‘lsa ham, u avtosalondan biror shaxs tomonidan xarid qilingan bo‘ladi va shu sababli u avtomobilning birinchi egasi hisoblanadi. Egalar soni maksimal 4 tagacha kiritilishi mumkin;
• Umumiy yurgan masofasi – avtomobilning umumiy bosib o'tgan yo'l masofasi kilometrda (masalan: 123000);
• Uzatma turi – avtomobilning transmissiyasi (mexanik yoki avtomat).
"""
    
    pdf.multi_cell(0, 8, additional_info)
    
    # Disclaimers with improved styling
    pdf.add_page()
    pdf.set_font('DejaVu', 'B', 18)
    pdf.set_text_color(0, 48, 73)  # Dark blue
    pdf.cell(0, 10, 'Muhim eslatmalar', 0, 1, 'L')
    
    pdf.set_font('DejaVu', '', 11)
    pdf.set_text_color(51, 51, 51)  # Dark gray
    disclaimers = """1. Ushbu hisobot faqat ma'lumot berish maqsadida taqdim etiladi va rasmiy baholash hisoboti sifatida ishlatilishi mumkin emas.
2. Bashorat qilingan narx joriy bozor ma'lumotlariga asoslangan bo'lib, haqiqiy savdo narxi farq qilishi mumkin.
3. Baholash natijasi ko'chmas mulkning haqiqiy holatini to'liq aks ettirmasligi mumkin, chunki baholash faqat kiritilgan ma'lumotlarga asoslanadi.
4. Ushbu baholash natijasidan moliyaviy va yuridik qarorlar qabul qilishda foydalanish tavsiya etilmaydi.

Model yangi ma'lumotlar bilan doimiy ravishda yangilanadi, bu esa uning aniqroq baholashini ta'minlaydi.

Hisoblangan narx ko'rsatilgan baholash yili va baholash oyi uchun haqiqiy hisoblanadi. Yuqorida ta'kidlanganidek model doimiy mukammallashib boradi va platformadan foydalanilgan sana va vaqtga qarab bir xil mulk bir xil baholash yili va oyi uchun turlicha qiymatni chiqarishi mumkin."""
    
    pdf.multi_cell(0, 8, disclaimers)

    # Create a bytes buffer and save the PDF to it
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_bytes = pdf_buffer.getvalue()
    pdf_buffer.close()
    
    return pdf_bytes