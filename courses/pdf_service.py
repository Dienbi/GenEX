"""
Service de génération de PDF pour les cours
"""
import os
import io
from django.conf import settings
from django.template.loader import render_to_string
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
import logging

logger = logging.getLogger(__name__)

class CoursePDFGenerator:
    """Générateur de PDF pour les cours"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configure les styles personnalisés pour le PDF"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CourseTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#dc3545'),
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les sections
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=20,
            textColor=HexColor('#333333'),
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les sous-sections
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=HexColor('#555555'),
            fontName='Helvetica-Bold'
        ))
        
        # Style pour le contenu
        self.styles.add(ParagraphStyle(
            name='Content',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Helvetica'
        ))
        
        # Style pour les métadonnées
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            textColor=HexColor('#666666'),
            fontName='Helvetica'
        ))
    
    def generate_course_pdf(self, course, sections):
        """Génère un PDF pour un cours donné"""
        try:
            # Créer un buffer en mémoire pour le PDF
            buffer = io.BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Construire le contenu du PDF
            story = []
            
            # En-tête du cours
            story.append(Paragraph(course.title, self.styles['CourseTitle']))
            story.append(Spacer(1, 20))
            
            # Métadonnées du cours
            metadata_text = f"""
            <b>Créé par :</b> {course.user.username}<br/>
            <b>Date de création :</b> {course.created_at.strftime('%d/%m/%Y à %H:%M')}<br/>
            <b>Langue :</b> {course.language.upper()}<br/>
            <b>Généré par IA :</b> {'Oui' if course.is_generated else 'Non'}
            """
            story.append(Paragraph(metadata_text, self.styles['Metadata']))
            story.append(Spacer(1, 30))
            
            # Table des matières
            if sections:
                story.append(Paragraph("Table des matières", self.styles['SectionTitle']))
                story.append(Spacer(1, 15))
                
                for i, section in enumerate(sections, 1):
                    toc_text = f"{i}. {section['title']}"
                    story.append(Paragraph(toc_text, self.styles['Content']))
                
                story.append(PageBreak())
            
            # Contenu des sections
            for i, section in enumerate(sections, 1):
                # Titre de la section
                story.append(Paragraph(f"{i}. {section['title']}", self.styles['SectionTitle']))
                
                # Contenu de la section
                if section.get('content'):
                    # Nettoyer le contenu HTML pour le PDF
                    content = self._clean_html_content(section['content'])
                    story.append(Paragraph(content, self.styles['Content']))
                
                # Ajouter un espacement entre les sections
                if i < len(sections):
                    story.append(Spacer(1, 20))
            
            # Pied de page
            story.append(Spacer(1, 30))
            footer_text = f"Généré le {course.updated_at.strftime('%d/%m/%Y à %H:%M')} - GenEX Platform"
            story.append(Paragraph(footer_text, self.styles['Metadata']))
            
            # Construire le PDF
            doc.build(story)
            
            # Récupérer le contenu du buffer
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du PDF: {str(e)}")
            raise e
    
    def _clean_html_content(self, html_content):
        """Nettoie le contenu HTML pour le PDF"""
        import re
        
        # Supprimer les balises HTML
        clean_text = re.sub(r'<[^>]+>', '', html_content)
        
        # Remplacer les entités HTML
        clean_text = clean_text.replace('&nbsp;', ' ')
        clean_text = clean_text.replace('&amp;', '&')
        clean_text = clean_text.replace('&lt;', '<')
        clean_text = clean_text.replace('&gt;', '>')
        clean_text = clean_text.replace('&quot;', '"')
        
        # Nettoyer les espaces multiples
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        return clean_text.strip()
    
    def save_course_pdf(self, course, sections, filename=None):
        """Sauvegarde le PDF du cours sur le disque"""
        try:
            # Générer le PDF
            pdf_content = self.generate_course_pdf(course, sections)
            
            # Définir le nom du fichier
            if not filename:
                safe_title = "".join(c for c in course.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"course_{course.id}_{safe_title}.pdf"
            
            # Chemin de sauvegarde
            pdf_dir = os.path.join(settings.MEDIA_ROOT, 'courses', 'pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            
            pdf_path = os.path.join(pdf_dir, filename)
            
            # Sauvegarder le fichier
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            
            # Retourner le chemin relatif
            relative_path = os.path.join('courses', 'pdfs', filename)
            return relative_path
            
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du PDF: {str(e)}")
            raise e

def generate_course_pdf_response(course, sections, filename=None):
    """Génère une réponse HTTP avec le PDF du cours"""
    try:
        generator = CoursePDFGenerator()
        pdf_content = generator.generate_course_pdf(course, sections)
        
        # Définir le nom du fichier
        if not filename:
            safe_title = "".join(c for c in course.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}.pdf"
        
        # Créer la réponse HTTP
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération de la réponse PDF: {str(e)}")
        raise e
