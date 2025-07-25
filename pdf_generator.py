try:
    from fpdf import FPDF
except ImportError:
    try:
        from fpdf2 import FPDF
    except ImportError:
        # If neither works, create a simple fallback
        class FPDF:
            def __init__(self):
                pass
            def add_page(self):
                pass
            def set_font(self, *args):
                pass
            def cell(self, *args):
                pass
            def ln(self, *args):
                pass
            def output(self, *args):
                return b'PDF generation not available'

import os
from datetime import datetime

def create_report(property_details, predicted_price, price_range):
    """
    Create a PDF report for apartment evaluation
    
    Args:
        property_details (dict): Dictionary with property information
        predicted_price (str): Predicted price value
        price_range (str): Price range string
    
    Returns:
        bytes: PDF file as bytes
    """
    print(f"DEBUG: Starting PDF generation with price: {predicted_price}, range: {price_range}")
    print(f"DEBUG: Property details: {property_details}")
    
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Simple test content first
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'APARTMENT EVALUATION REPORT', 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f'Date: {datetime.now().strftime("%d/%m/%Y")}', 0, 1, 'L')
        pdf.ln(5)
        
        # Add property details
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'PROPERTY INFORMATION', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 10)
        
        # Add each property detail
        for key, value in property_details.items():
            if value and str(value).strip():
                pdf.cell(0, 6, f'{key}: {str(value)}', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Evaluation Results
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'EVALUATION RESULTS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        
        # Price information
        try:
            price_formatted = f'${int(predicted_price):,}' if predicted_price else 'N/A'
        except (ValueError, TypeError):
            price_formatted = f'${predicted_price}' if predicted_price else 'N/A'
        
        pdf.cell(0, 8, f'Estimated Price: {price_formatted}', 0, 1, 'L')
        pdf.cell(0, 8, f'Price Range: {str(price_range) if price_range else "N/A"}', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Footer
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, 'Accuracy: +/- 3.61%', 0, 1, 'L')
        pdf.cell(0, 6, 'This report was generated using AI technology.', 0, 1, 'L')
        
        print("DEBUG: PDF content added successfully")
        
        # Generate PDF bytes - fpdf2 returns bytearray
        pdf_output = pdf.output()
        print(f"DEBUG: PDF output type: {type(pdf_output)}, length: {len(pdf_output) if pdf_output else 0}")
        
        # Convert bytearray to bytes
        if isinstance(pdf_output, bytearray):
            return bytes(pdf_output)
        else:
            return pdf_output
        
    except Exception as e:
        print(f"DEBUG: Error in PDF generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return b'PDF generation error' 