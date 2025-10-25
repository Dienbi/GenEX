import os
import io
from typing import Tuple, Optional
import PyPDF2
import pandas as pd
from openpyxl import load_workbook
from django.core.files.uploadedfile import UploadedFile as DjangoUploadedFile


class FileProcessor:
    """Service pour traiter les fichiers PDF et Excel"""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_PDF_EXTENSIONS = ['.pdf']
    SUPPORTED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']
    
    @classmethod
    def is_supported_file(cls, filename: str) -> bool:
        """Vérifie si le fichier est supporté"""
        ext = os.path.splitext(filename)[1].lower()
        return ext in cls.SUPPORTED_PDF_EXTENSIONS + cls.SUPPORTED_EXCEL_EXTENSIONS
    
    @classmethod
    def get_file_type(cls, filename: str) -> str:
        """Détermine le type de fichier"""
        ext = os.path.splitext(filename)[1].lower()
        if ext in cls.SUPPORTED_PDF_EXTENSIONS:
            return 'pdf'
        elif ext in cls.SUPPORTED_EXCEL_EXTENSIONS:
            return 'excel'
        else:
            return 'other'
    
    @classmethod
    def validate_file(cls, file: DjangoUploadedFile) -> Tuple[bool, str]:
        """Valide un fichier uploadé"""
        if file.size > cls.MAX_FILE_SIZE:
            return False, f"Le fichier est trop volumineux. Taille maximale: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
        
        if not cls.is_supported_file(file.name):
            return False, "Type de fichier non supporté. Formats acceptés: PDF, Excel (.xlsx, .xls)"
        
        return True, "Fichier valide"
    
    @classmethod
    def extract_pdf_content(cls, file: DjangoUploadedFile) -> str:
        """Extrait le contenu textuel d'un PDF"""
        try:
            # Lire le fichier PDF
            pdf_reader = PyPDF2.PdfReader(file)
            text_content = []
            
            # Extraire le texte de chaque page
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{text}")
            
            return "\n\n".join(text_content)
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction du PDF: {str(e)}")
    
    @classmethod
    def extract_excel_content(cls, file: DjangoUploadedFile) -> str:
        """Extrait le contenu d'un fichier Excel"""
        try:
            # Lire le fichier Excel
            df = pd.read_excel(file, sheet_name=None)  # None = toutes les feuilles
            
            content_parts = []
            
            for sheet_name, sheet_data in df.items():
                content_parts.append(f"=== Feuille: {sheet_name} ===")
                
                # Informations sur la feuille
                content_parts.append(f"Dimensions: {sheet_data.shape[0]} lignes x {sheet_data.shape[1]} colonnes")
                content_parts.append("")
                
                # En-têtes des colonnes
                if not sheet_data.empty:
                    content_parts.append("Colonnes:")
                    for col in sheet_data.columns:
                        content_parts.append(f"- {col}")
                    content_parts.append("")
                    
                    # Aperçu des données (premières lignes)
                    content_parts.append("Aperçu des données:")
                    preview = sheet_data.head(10)  # Premières 10 lignes
                    
                    # Convertir en texte formaté
                    for idx, row in preview.iterrows():
                        row_data = []
                        for col in sheet_data.columns:
                            value = row[col]
                            if pd.isna(value):
                                value = "[Vide]"
                            row_data.append(f"{col}: {value}")
                        content_parts.append(f"Ligne {idx + 1}: {' | '.join(row_data)}")
                    
                    content_parts.append("")
            
            return "\n".join(content_parts)
        
        except Exception as e:
            raise Exception(f"Erreur lors de l'extraction de l'Excel: {str(e)}")
    
    @classmethod
    def process_file(cls, file: DjangoUploadedFile) -> Tuple[str, str, int]:
        """Traite un fichier et retourne (contenu, type, taille)"""
        # Valider le fichier
        is_valid, message = cls.validate_file(file)
        if not is_valid:
            raise Exception(message)
        
        # Déterminer le type
        file_type = cls.get_file_type(file.name)
        
        # Extraire le contenu selon le type
        if file_type == 'pdf':
            content = cls.extract_pdf_content(file)
        elif file_type == 'excel':
            content = cls.extract_excel_content(file)
        else:
            content = "Contenu non extractible"
        
        return content, file_type, file.size
