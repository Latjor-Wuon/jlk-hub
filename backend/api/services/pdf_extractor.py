"""
PDF Text Extraction Service

Extracts text content from uploaded PDF files for lesson generation.
"""

import re
from typing import Optional, Tuple

# Try to import PDF libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


class PDFExtractorService:
    """Service for extracting text from PDF files"""
    
    @staticmethod
    def is_available() -> bool:
        """Check if PDF extraction is available"""
        return PDFPLUMBER_AVAILABLE or PYPDF2_AVAILABLE
    
    @staticmethod
    def extract_text(file_path: str, start_page: int = None, end_page: int = None) -> Tuple[str, dict]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            start_page: Optional starting page (1-indexed)
            end_page: Optional ending page (1-indexed)
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        metadata = {
            'total_pages': 0,
            'extracted_pages': 0,
            'method': None,
            'word_count': 0
        }
        
        text = ""
        
        # Try pdfplumber first (better for complex layouts)
        if PDFPLUMBER_AVAILABLE:
            try:
                text, metadata = PDFExtractorService._extract_with_pdfplumber(
                    file_path, start_page, end_page
                )
                if text.strip():
                    return text, metadata
            except Exception as e:
                metadata['pdfplumber_error'] = str(e)
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                text, metadata = PDFExtractorService._extract_with_pypdf2(
                    file_path, start_page, end_page
                )
            except Exception as e:
                metadata['pypdf2_error'] = str(e)
        
        if not text.strip():
            raise ValueError("Could not extract text from PDF. The file may be scanned/image-based.")
        
        return text, metadata
    
    @staticmethod
    def _extract_with_pdfplumber(file_path: str, start_page: int = None, end_page: int = None) -> Tuple[str, dict]:
        """Extract text using pdfplumber (better for tables and complex layouts)"""
        text_parts = []
        metadata = {
            'total_pages': 0,
            'extracted_pages': 0,
            'method': 'pdfplumber',
            'word_count': 0
        }
        
        with pdfplumber.open(file_path) as pdf:
            metadata['total_pages'] = len(pdf.pages)
            
            # Determine page range
            start_idx = (start_page - 1) if start_page else 0
            end_idx = end_page if end_page else len(pdf.pages)
            
            for i, page in enumerate(pdf.pages[start_idx:end_idx], start=start_idx + 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i} ---\n{page_text}")
                    metadata['extracted_pages'] += 1
        
        full_text = "\n\n".join(text_parts)
        full_text = PDFExtractorService._clean_text(full_text)
        metadata['word_count'] = len(full_text.split())
        
        return full_text, metadata
    
    @staticmethod
    def _extract_with_pypdf2(file_path: str, start_page: int = None, end_page: int = None) -> Tuple[str, dict]:
        """Extract text using PyPDF2 (fallback method)"""
        text_parts = []
        metadata = {
            'total_pages': 0,
            'extracted_pages': 0,
            'method': 'pypdf2',
            'word_count': 0
        }
        
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            metadata['total_pages'] = len(reader.pages)
            
            # Determine page range
            start_idx = (start_page - 1) if start_page else 0
            end_idx = end_page if end_page else len(reader.pages)
            
            for i in range(start_idx, min(end_idx, len(reader.pages))):
                page = reader.pages[i]
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {i + 1} ---\n{page_text}")
                    metadata['extracted_pages'] += 1
        
        full_text = "\n\n".join(text_parts)
        full_text = PDFExtractorService._clean_text(full_text)
        metadata['word_count'] = len(full_text.split())
        
        return full_text, metadata
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Clean extracted text while preserving document structure.
        Maintains headings, bullet points, paragraphs, and logical sections.
        """
        # Completely remove page markers - they should not appear in final output
        text = re.sub(r'---\s*Page\s*\d+\s*---', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'---\s*PAGE_BREAK\s*---', '\n\n', text, flags=re.IGNORECASE)
        text = re.sub(r'---\s*page_break\s*---', '\n\n', text, flags=re.IGNORECASE)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Process line by line to preserve structure
        lines = text.split('\n')
        processed_lines = []
        prev_line_empty = False
        
        for line in lines:
            stripped = line.strip()
            
            # Skip empty lines but mark as paragraph break
            if not stripped:
                if not prev_line_empty:
                    processed_lines.append('')
                    prev_line_empty = True
                continue
            
            # Skip lines that look like page artifacts
            if re.match(r'^(page\s*\d+|\d+\s*$|---+$)', stripped, re.IGNORECASE):
                continue
            
            prev_line_empty = False
            
            # Detect and preserve bullet points
            if re.match(r'^[\u2022\u2023\u25E6\u2043\u2219•●○◦▪▸►\-\*]\s*', stripped):
                bullet_content = re.sub(r'^[\u2022\u2023\u25E6\u2043\u2219•●○◦▪▸►\-\*]\s*', '', stripped)
                if bullet_content:  # Only add if there's actual content
                    processed_lines.append('• ' + bullet_content)
                continue
            
            # Detect numbered lists (1. or 1) or a. or a))
            if re.match(r'^(\d+[\.\)]\s*|[a-zA-Z][\.\)]\s*)', stripped):
                processed_lines.append(stripped)
                continue
            
            # Detect potential headings (short lines, possibly uppercase or title case)
            if len(stripped) < 80 and len(stripped) > 3:
                # Skip if it looks like a page number or artifact
                if stripped.isdigit():
                    continue
                    
                # All caps heading (but not single letters)
                if stripped.isupper() and len(stripped.split()) > 1:
                    processed_lines.append(f'\n## {stripped.title()}\n')
                    continue
                    
                # Title case with 2-8 words - likely a heading
                words = stripped.split()
                if 2 <= len(words) <= 8 and stripped.istitle():
                    processed_lines.append(f'\n### {stripped}\n')
                    continue
                    
                # Lines ending with colon often indicate section headers
                if stripped.endswith(':') and len(stripped) < 60:
                    processed_lines.append(f'\n### {stripped}\n')
                    continue
            
            # Regular content line - clean up excessive spaces
            cleaned_line = re.sub(r'\s{2,}', ' ', stripped)
            processed_lines.append(cleaned_line)
        
        text = '\n'.join(processed_lines)
        
        # Consolidate multiple blank lines
        text = re.sub(r'\n{4,}', '\n\n\n', text)
        
        # Clean up heading spacing
        text = re.sub(r'\n{2,}(##)', r'\n\n\1', text)
        
        return text.strip()
    
    @staticmethod
    def _detect_document_structure(text: str) -> dict:
        """
        Analyze the document structure to identify key elements.
        Returns metadata about detected structure.
        """
        structure = {
            'has_headings': bool(re.search(r'^##\s+.+$', text, re.MULTILINE)),
            'has_bullet_points': bool(re.search(r'^[•\-]\s+.+$', text, re.MULTILINE)),
            'has_numbered_lists': bool(re.search(r'^\d+[\.\)]\s+.+$', text, re.MULTILINE)),
            'paragraph_count': len(re.findall(r'\n\n[^\n]', text)),
            'potential_sections': []
        }
        
        # Find potential section headings
        headings = re.findall(r'^##\s+(.+)$|^###\s+(.+)$', text, re.MULTILINE)
        structure['potential_sections'] = [h[0] or h[1] for h in headings]
        
        return structure
    
    @staticmethod
    def extract_from_django_file(file_field) -> Tuple[str, dict]:
        """
        Extract text from a Django FileField.
        
        Args:
            file_field: Django FileField or UploadedFile
            
        Returns:
            Tuple of (extracted_text, metadata)
        """
        if hasattr(file_field, 'path'):
            # FileField with path
            return PDFExtractorService.extract_text(file_field.path)
        elif hasattr(file_field, 'temporary_file_path'):
            # TemporaryUploadedFile
            return PDFExtractorService.extract_text(file_field.temporary_file_path())
        else:
            # InMemoryUploadedFile - need to save temporarily
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                for chunk in file_field.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            try:
                return PDFExtractorService.extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)
