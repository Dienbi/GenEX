from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os
from django.conf import settings
from datetime import datetime

class PDFGenerator:
    @staticmethod
    def generate_pdf(content, title="Document généré", filename="document.pdf"):
        """
        Génère un PDF avec une mise en page professionnelle
        """
        buffer = BytesIO()
        
        # Créer le document PDF avec des marges optimisées
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        
        # Styles professionnels
        styles = getSampleStyleSheet()
        
        # Style pour le titre principal
        title_style = ParagraphStyle(
            'MainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=10,
            backColor=colors.HexColor('#ecf0f1')
        )
        
        # Style pour les sous-titres
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=15,
            spaceBefore=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold',
            borderWidth=0.5,
            borderColor=colors.HexColor('#bdc3c7'),
            borderPadding=5,
            leftIndent=10
        )
        
        # Style pour le contenu principal
        content_style = ParagraphStyle(
            'MainContent',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=5,
            alignment=TA_JUSTIFY,
            leftIndent=15,
            rightIndent=15,
            fontName='Helvetica',
            lineHeight=1.4,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Style pour les listes
        list_style = ParagraphStyle(
            'ListContent',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=3,
            alignment=TA_LEFT,
            leftIndent=25,
            fontName='Helvetica',
            textColor=colors.HexColor('#34495e')
        )
        
        # Style pour les citations
        quote_style = ParagraphStyle(
            'Quote',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            spaceBefore=10,
            alignment=TA_LEFT,
            leftIndent=30,
            rightIndent=30,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#7f8c8d'),
            borderWidth=1,
            borderColor=colors.HexColor('#bdc3c7'),
            borderPadding=10,
            backColor=colors.HexColor('#f8f9fa')
        )
        
        # Style pour le pied de page
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#95a5a6'),
            fontName='Helvetica'
        )
        
        # Construire le contenu du PDF
        story = []
        
        # En-tête avec titre
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 15))
        
        # Date de génération
        current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        story.append(Paragraph(f"<i>Généré le {current_date}</i>", footer_style))
        story.append(Spacer(1, 20))
        
        # Traiter le contenu avec une mise en page améliorée
        if isinstance(content, str):
            paragraphs = content.split('\n\n')
            
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if paragraph:
                    # Détecter les différents types de contenu
                    if paragraph.startswith('###'):
                        # Sous-sous-titre
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(f"<b>{clean_text}</b>", content_style))
                    elif paragraph.startswith('##'):
                        # Sous-titre
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(clean_text, subtitle_style))
                    elif paragraph.startswith('#'):
                        # Titre principal
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(clean_text, subtitle_style))
                    elif paragraph.startswith('- ') or paragraph.startswith('• '):
                        # Liste à puces
                        clean_text = paragraph.lstrip('- •').strip()
                        story.append(Paragraph(f"• {clean_text}", list_style))
                    elif paragraph.startswith('>'):
                        # Citation
                        clean_text = paragraph.lstrip('>').strip()
                        story.append(Paragraph(f'"{clean_text}"', quote_style))
                    else:
                        # Paragraphe normal
                        story.append(Paragraph(paragraph, content_style))
                    
                    # Ajouter un espacement approprié
                    if i < len(paragraphs) - 1:
                        story.append(Spacer(1, 8))
        else:
            # Si le contenu n'est pas une string, le convertir
            story.append(Paragraph(str(content), content_style))
        
        # Pied de page
        story.append(Spacer(1, 30))
        story.append(Paragraph("─" * 50, footer_style))
        story.append(Spacer(1, 5))
        story.append(Paragraph("Document généré par GenEX Assistant Éducatif", footer_style))
        story.append(Paragraph("Plateforme d'apprentissage intelligente", footer_style))
        
        # Construire le PDF
        doc.build(story)
        
        # Récupérer le contenu du buffer
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
    
    @staticmethod
    def generate_educational_pdf(topic, content, level="intermédiaire"):
        """
        Génère un PDF éducatif avec une mise en page professionnelle
        """
        buffer = BytesIO()
        
        # Créer le document PDF avec des marges optimisées
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2*cm
        )
        
        styles = getSampleStyleSheet()
        
        # Styles éducatifs professionnels
        title_style = ParagraphStyle(
            'EducationalTitle',
            parent=styles['Heading1'],
            fontSize=26,
            spaceAfter=25,
            spaceBefore=15,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=15,
            backColor=colors.HexColor('#ecf0f1')
        )
        
        # Style pour le niveau
        level_style = ParagraphStyle(
            'Level',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            spaceBefore=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#e74c3c'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#e74c3c'),
            borderPadding=8,
            backColor=colors.HexColor('#fdf2f2')
        )
        
        # Style pour les sections principales
        section_style = ParagraphStyle(
            'EducationalSection',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#2c3e50'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3498db'),
            borderPadding=8,
            leftIndent=10,
            backColor=colors.HexColor('#f8f9fa')
        )
        
        # Style pour les sous-sections
        subsection_style = ParagraphStyle(
            'EducationalSubsection',
            parent=styles['Heading3'],
            fontSize=13,
            spaceAfter=8,
            spaceBefore=15,
            alignment=TA_LEFT,
            textColor=colors.HexColor('#34495e'),
            fontName='Helvetica-Bold',
            leftIndent=20,
            borderWidth=0.5,
            borderColor=colors.HexColor('#bdc3c7'),
            borderPadding=5
        )
        
        # Style pour le contenu éducatif
        content_style = ParagraphStyle(
            'EducationalContent',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            spaceBefore=5,
            alignment=TA_JUSTIFY,
            leftIndent=15,
            rightIndent=15,
            fontName='Helvetica',
            lineHeight=1.5,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Style pour les points importants
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            spaceBefore=8,
            alignment=TA_LEFT,
            leftIndent=25,
            fontName='Helvetica-Bold',
            textColor=colors.HexColor('#e74c3c'),
            backColor=colors.HexColor('#fdf2f2'),
            borderWidth=1,
            borderColor=colors.HexColor('#fadbd8'),
            borderPadding=8
        )
        
        # Style pour le pied de page
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#95a5a6'),
            fontName='Helvetica'
        )
        
        # Construire le contenu
        story = []
        
        # En-tête éducatif
        story.append(Paragraph(f"📚 {topic}", title_style))
        story.append(Paragraph(f"Niveau : {level.title()}", level_style))
        story.append(Spacer(1, 20))
        
        # Date de génération
        current_date = datetime.now().strftime("%d/%m/%Y à %H:%M")
        story.append(Paragraph(f"<i>Généré le {current_date}</i>", footer_style))
        story.append(Spacer(1, 25))
        
        # Contenu principal avec mise en page éducative
        if isinstance(content, str):
            paragraphs = content.split('\n\n')
            
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if paragraph:
                    # Détecter les différents types de contenu éducatif
                    if paragraph.startswith('###'):
                        # Sous-sous-section
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(f"<b>{clean_text}</b>", content_style))
                    elif paragraph.startswith('##'):
                        # Sous-section
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(clean_text, subsection_style))
                    elif paragraph.startswith('#'):
                        # Section principale
                        clean_text = paragraph.lstrip('#').strip()
                        story.append(Paragraph(clean_text, section_style))
                    elif paragraph.startswith('⚠️') or paragraph.startswith('💡') or paragraph.startswith('📌'):
                        # Points importants
                        story.append(Paragraph(paragraph, highlight_style))
                    elif paragraph.startswith('- ') or paragraph.startswith('• '):
                        # Liste à puces
                        clean_text = paragraph.lstrip('- •').strip()
                        story.append(Paragraph(f"• {clean_text}", content_style))
                    else:
                        # Contenu normal
                        story.append(Paragraph(paragraph, content_style))
                    
                    # Ajouter un espacement approprié
                    if i < len(paragraphs) - 1:
                        story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(str(content), content_style))
        
        # Pied de page éducatif
        story.append(Spacer(1, 30))
        story.append(Paragraph("═" * 60, footer_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph("📖 Document éducatif généré par GenEX Assistant", footer_style))
        story.append(Paragraph("🎓 Plateforme d'apprentissage intelligente", footer_style))
        story.append(Paragraph("💡 Optimisé pour l'apprentissage et la compréhension", footer_style))
        
        doc.build(story)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        return pdf_content
