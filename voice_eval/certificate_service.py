"""Service for generating PDF certificates with QR codes"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO
from PIL import Image
from django.conf import settings
from datetime import datetime
import os


class CertificateGenerator:
    """Generate professional certificates for language evaluation"""
    
    def __init__(self):
        self.width, self.height = A4
        self.margin = 0.75 * inch
    
    def generate_certificate(self, user, evaluation, certificate_id):
        """
        Generate a PDF certificate for a user's evaluation
        
        Args:
            user: User object
            evaluation: VoiceEvaluation object
            certificate_id: UUID for the certificate
            
        Returns:
            BytesIO buffer containing the PDF
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        # Add border
        self._add_border(c)
        
        # Add header
        self._add_header(c)
        
        # Add certificate title
        self._add_title(c)
        
        # Add user information
        self._add_user_info(c, user, evaluation)
        
        # Add score details
        self._add_score_details(c, evaluation)
        
        # Add credits/message
        self._add_credits(c, evaluation)
        
        # Add QR code
        self._add_qr_code(c, certificate_id)
        
        # Add footer
        self._add_footer(c, certificate_id, evaluation.created_at)
        
        c.save()
        buffer.seek(0)
        return buffer
    
    def _add_border(self, c):
        """Add decorative border"""
        # Outer border - red
        c.setStrokeColor(colors.HexColor('#dc3545'))
        c.setLineWidth(3)
        c.rect(self.margin - 10, self.margin - 10, 
               self.width - 2 * (self.margin - 10), 
               self.height - 2 * (self.margin - 10))
        
        # Inner border - black
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.rect(self.margin, self.margin, 
               self.width - 2 * self.margin, 
               self.height - 2 * self.margin)
    
    def _add_header(self, c):
        """Add GenEx logo and header"""
        # GENEX title
        c.setFont("Helvetica-Bold", 36)
        c.setFillColor(colors.HexColor('#dc3545'))
        c.drawCentredString(self.width / 2, self.height - self.margin - 40, "GENEX")
        
        # Subtitle
        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawCentredString(self.width / 2, self.height - self.margin - 60, 
                           "Platform for Language Excellence")
    
    def _add_title(self, c):
        """Add certificate title"""
        c.setFont("Helvetica-Bold", 28)
        c.setFillColor(colors.black)
        c.drawCentredString(self.width / 2, self.height - self.margin - 120, 
                           "Certificate of Achievement")
        
        # Decorative line
        c.setStrokeColor(colors.HexColor('#dc3545'))
        c.setLineWidth(2)
        line_start = self.width / 2 - 150
        line_end = self.width / 2 + 150
        c.line(line_start, self.height - self.margin - 130, 
               line_end, self.height - self.margin - 130)
    
    def _add_user_info(self, c, user, evaluation):
        """Add user information"""
        y_position = self.height - self.margin - 180
        
        # "This certifies that"
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        c.drawCentredString(self.width / 2, y_position, "This certifies that")
        
        # User name
        y_position -= 35
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor('#dc3545'))
        full_name = f"{user.first_name} {user.last_name}" if user.first_name else user.username
        c.drawCentredString(self.width / 2, y_position, full_name)
        
        # Name underline
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        name_width = c.stringWidth(full_name, "Helvetica-Bold", 20)
        c.line(self.width / 2 - name_width / 2 - 20, y_position - 5,
               self.width / 2 + name_width / 2 + 20, y_position - 5)
    
    def _add_score_details(self, c, evaluation):
        """Add evaluation score details"""
        y_position = self.height - self.margin - 270
        
        # Achievement text
        c.setFont("Helvetica", 14)
        c.setFillColor(colors.black)
        
        language_name = "English" if evaluation.language == 'en' else "French"
        level_name = dict(evaluation.LEVEL_CHOICES).get(evaluation.estimated_level, evaluation.estimated_level)
        
        text = f"has successfully demonstrated {language_name} language proficiency"
        c.drawCentredString(self.width / 2, y_position, text)
        
        y_position -= 25
        text = f"at {level_name} level"
        c.drawCentredString(self.width / 2, y_position, text)
        
        # Score box
        y_position -= 50
        box_width = 300
        box_height = 80
        box_x = (self.width - box_width) / 2
        
        # Score box background
        c.setFillColor(colors.HexColor('#f8f9fa'))
        c.rect(box_x, y_position - box_height, box_width, box_height, fill=1)
        
        # Score box border
        c.setStrokeColor(colors.HexColor('#dc3545'))
        c.setLineWidth(2)
        c.rect(box_x, y_position - box_height, box_width, box_height, fill=0)
        
        # Overall score
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(colors.black)
        c.drawCentredString(self.width / 2, y_position - 25, "Overall Score")
        
        c.setFont("Helvetica-Bold", 32)
        c.setFillColor(colors.HexColor('#dc3545'))
        c.drawCentredString(self.width / 2, y_position - 60, f"{evaluation.total_score:.0f}/100")
    
    def _add_credits(self, c, evaluation):
        """Add congratulatory message"""
        y_position = self.height - self.margin - 440
        
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.black)
        
        # Determine message based on score
        score = evaluation.total_score
        if score >= 90:
            message = ("Exceptional performance! Your outstanding language skills demonstrate "
                      "mastery and excellence in communication. Continue inspiring others with your expertise.")
        elif score >= 80:
            message = ("Excellent work! Your strong language abilities reflect dedication and skill. "
                      "Keep up the great work in your language learning journey.")
        elif score >= 70:
            message = ("Great achievement! Your solid language proficiency shows consistent progress. "
                      "Continue building on this strong foundation.")
        else:
            message = ("Congratulations on completing your evaluation. "
                      "Keep practicing to enhance your language skills further.")
        
        # Split message into lines
        max_width = self.width - 2 * self.margin - 80
        words = message.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if c.stringWidth(test_line, "Helvetica", 11) <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for i, line in enumerate(lines):
            c.drawCentredString(self.width / 2, y_position - i * 15, line)
    
    def _add_qr_code(self, c, certificate_id):
        """Add QR code linking to platform"""
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        # Link to home page
        qr_url = f"{settings.SITE_URL or 'http://127.0.0.1:8000'}/"
        qr.add_data(qr_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        qr_buffer = BytesIO()
        img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        
        # Add to PDF - use ImageReader for BytesIO
        from reportlab.lib.utils import ImageReader
        qr_size = 80
        x = self.width - self.margin - qr_size - 20
        y = self.margin + 40
        
        c.drawImage(ImageReader(qr_buffer), x, y, width=qr_size, height=qr_size)
        
        # QR code label
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.black)
        c.drawCentredString(x + qr_size / 2, y - 10, "Scan to visit")
        c.drawCentredString(x + qr_size / 2, y - 20, "GENEX Platform")
    
    def _add_footer(self, c, certificate_id, issue_date):
        """Add footer with certificate details"""
        y_position = self.margin + 60
        
        # Certificate ID
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawString(self.margin + 20, y_position, f"Certificate ID: {str(certificate_id)[:18]}...")
        
        # Issue date
        date_str = issue_date.strftime("%B %d, %Y")
        c.drawString(self.margin + 20, y_position - 15, f"Issued on: {date_str}")
        
        # Signature line
        y_position -= 40
        sig_width = 150
        sig_x = self.width / 2 - sig_width / 2
        
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        c.line(sig_x, y_position, sig_x + sig_width, y_position)
        
        c.setFont("Helvetica-Bold", 10)
        c.setFillColor(colors.black)
        c.drawCentredString(self.width / 2, y_position - 15, "GENEX Platform Director")
        
        # Verification text
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor('#666666'))
        c.drawCentredString(self.width / 2, self.margin + 15, 
                           "This certificate can be verified at www.genex-platform.com")


# Global instance
certificate_generator = CertificateGenerator()
