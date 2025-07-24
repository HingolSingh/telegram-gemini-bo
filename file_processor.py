"""
File processing utilities for handling various file types.
"""
import logging
import tempfile
import os
import io
from typing import Optional, Dict, Any
import magic
import asyncio

logger = logging.getLogger(__name__)


class FileProcessor:
    """Handle processing of various file types."""
    
    def __init__(self):
        self.supported_types = {
            'application/pdf': self._process_pdf,
            'text/plain': self._process_text,
            'application/json': self._process_json,
            'text/csv': self._process_csv,
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': self._process_docx,
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': self._process_xlsx,
            'text/markdown': self._process_markdown,
            'application/x-python': self._process_code,
            'text/x-python': self._process_code,
            'application/javascript': self._process_code,
            'text/javascript': self._process_code,
            'text/html': self._process_html,
            'text/xml': self._process_xml
        }
    
    async def process_file(self, file_data: bytes, filename: str, file_type: str = None) -> str:
        """Process file based on its type."""
        try:
            # Detect file type if not provided
            if not file_type:
                file_type = magic.from_buffer(file_data, mime=True)
            
            logger.info(f"Processing file: {filename}, type: {file_type}")
            
            # Check if we support this file type
            if file_type in self.supported_types:
                processor = self.supported_types[file_type]
                result = await processor(file_data, filename)
                return result
            else:
                # Fallback for unsupported types
                return await self._process_unknown(file_data, filename, file_type)
                
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return f"Error processing file: {str(e)}"
    
    async def _process_pdf(self, file_data: bytes, filename: str) -> str:
        """Process PDF files."""
        try:
            import PyPDF2
            
            with io.BytesIO(file_data) as pdf_stream:
                pdf_reader = PyPDF2.PdfReader(pdf_stream)
                text_content = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text_content += f"\n--- Page {page_num + 1} ---\n"
                    text_content += page.extract_text()
                
                if not text_content.strip():
                    return "PDF processed but no readable text found. This might be a scanned document or image-based PDF."
                
                summary = f"📄 **PDF Analysis: {filename}**\n\n"
                summary += f"**Pages:** {len(pdf_reader.pages)}\n"
                summary += f"**Content Preview:**\n{text_content[:2000]}..."
                
                if len(text_content) > 2000:
                    summary += f"\n\n*Total content: {len(text_content)} characters*"
                
                return summary
                
        except ImportError:
            return "PDF processing requires PyPDF2. Please install it: pip install PyPDF2"
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
    
    async def _process_text(self, file_data: bytes, filename: str) -> str:
        """Process plain text files."""
        try:
            text_content = file_data.decode('utf-8', errors='ignore')
            
            # Basic analysis
            lines = text_content.split('\n')
            words = len(text_content.split())
            chars = len(text_content)
            
            summary = f"📝 **Text File Analysis: {filename}**\n\n"
            summary += f"**Statistics:**\n"
            summary += f"• Lines: {len(lines)}\n"
            summary += f"• Words: {words}\n"
            summary += f"• Characters: {chars}\n\n"
            
            if chars <= 1000:
                summary += f"**Content:**\n```\n{text_content}\n```"
            else:
                summary += f"**Content Preview:**\n```\n{text_content[:1000]}...\n```"
                summary += f"\n*File is large. Showing first 1000 characters.*"
            
            return summary
            
        except Exception as e:
            return f"Error processing text file: {str(e)}"
    
    async def _process_json(self, file_data: bytes, filename: str) -> str:
        """Process JSON files."""
        try:
            import json
            
            text_content = file_data.decode('utf-8', errors='ignore')
            json_data = json.loads(text_content)
            
            summary = f"📊 **JSON Analysis: {filename}**\n\n"
            
            # Analyze structure
            if isinstance(json_data, dict):
                summary += f"**Type:** Object with {len(json_data)} keys\n"
                summary += f"**Keys:** {', '.join(list(json_data.keys())[:10])}\n"
                if len(json_data) > 10:
                    summary += "... (showing first 10 keys)\n"
            elif isinstance(json_data, list):
                summary += f"**Type:** Array with {len(json_data)} items\n"
                if json_data and isinstance(json_data[0], dict):
                    summary += f"**Item structure:** {list(json_data[0].keys())}\n"
            
            # Pretty print preview
            preview = json.dumps(json_data, indent=2)[:1500]
            summary += f"\n**Content Preview:**\n```json\n{preview}\n```"
            
            if len(preview) >= 1500:
                summary += "\n*Large file. Showing preview only.*"
            
            return summary
            
        except json.JSONDecodeError as e:
            return f"Invalid JSON file: {str(e)}"
        except Exception as e:
            return f"Error processing JSON: {str(e)}"
    
    async def _process_csv(self, file_data: bytes, filename: str) -> str:
        """Process CSV files."""
        try:
            import pandas as pd
            
            # Try to read as CSV
            with io.StringIO(file_data.decode('utf-8', errors='ignore')) as csv_stream:
                df = pd.read_csv(csv_stream)
            
            summary = f"📈 **CSV Analysis: {filename}**\n\n"
            summary += f"**Dimensions:** {df.shape[0]} rows, {df.shape[1]} columns\n"
            summary += f"**Columns:** {', '.join(df.columns.tolist())}\n\n"
            
            # Data types
            summary += "**Data Types:**\n"
            for col, dtype in df.dtypes.items():
                summary += f"• {col}: {dtype}\n"
            
            # Preview
            summary += f"\n**Data Preview:**\n```\n{df.head().to_string()}\n```"
            
            # Basic statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary += f"\n**Numeric Summary:**\n```\n{df[numeric_cols].describe().to_string()}\n```"
            
            return summary
            
        except Exception as e:
            return f"Error processing CSV: {str(e)}"
    
    async def _process_code(self, file_data: bytes, filename: str) -> str:
        """Process code files."""
        try:
            code_content = file_data.decode('utf-8', errors='ignore')
            lines = code_content.split('\n')
            
            # Basic code analysis
            non_empty_lines = [line for line in lines if line.strip()]
            comment_lines = [line for line in lines if line.strip().startswith(('#', '//', '/*', '"""', "'''"))]
            
            # Detect language
            extension = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
            language_map = {
                'py': 'Python',
                'js': 'JavaScript',
                'ts': 'TypeScript',
                'java': 'Java',
                'cpp': 'C++',
                'c': 'C',
                'html': 'HTML',
                'css': 'CSS',
                'sql': 'SQL'
            }
            language = language_map.get(extension, extension.upper())
            
            summary = f"💻 **Code Analysis: {filename}**\n\n"
            summary += f"**Language:** {language}\n"
            summary += f"**Total lines:** {len(lines)}\n"
            summary += f"**Code lines:** {len(non_empty_lines)}\n"
            summary += f"**Comment lines:** {len(comment_lines)}\n\n"
            
            # Show code preview
            preview_lines = min(50, len(lines))
            summary += f"**Code Preview:**\n```{extension}\n"
            summary += '\n'.join(lines[:preview_lines])
            summary += "\n```"
            
            if len(lines) > 50:
                summary += f"\n*Showing first {preview_lines} lines of {len(lines)} total.*"
            
            return summary
            
        except Exception as e:
            return f"Error processing code file: {str(e)}"
    
    async def _process_html(self, file_data: bytes, filename: str) -> str:
        """Process HTML files."""
        try:
            from bs4 import BeautifulSoup
            
            html_content = file_data.decode('utf-8', errors='ignore')
            soup = BeautifulSoup(html_content, 'html.parser')
            
            summary = f"🌐 **HTML Analysis: {filename}**\n\n"
            
            # Extract metadata
            title = soup.find('title')
            summary += f"**Title:** {title.get_text() if title else 'No title'}\n"
            
            # Count elements
            summary += f"**Structure:**\n"
            summary += f"• Links: {len(soup.find_all('a'))}\n"
            summary += f"• Images: {len(soup.find_all('img'))}\n"
            summary += f"• Forms: {len(soup.find_all('form'))}\n"
            summary += f"• Scripts: {len(soup.find_all('script'))}\n"
            summary += f"• Stylesheets: {len(soup.find_all('link', rel='stylesheet'))}\n"
            
            # Extract text content
            text_content = soup.get_text()[:1000]
            summary += f"\n**Text Content Preview:**\n{text_content}..."
            
            return summary
            
        except ImportError:
            return "HTML processing requires BeautifulSoup. Please install it: pip install beautifulsoup4"
        except Exception as e:
            return f"Error processing HTML: {str(e)}"
    
    async def _process_xml(self, file_data: bytes, filename: str) -> str:
        """Process XML files."""
        try:
            import xml.etree.ElementTree as ET
            
            xml_content = file_data.decode('utf-8', errors='ignore')
            root = ET.fromstring(xml_content)
            
            summary = f"🗂️ **XML Analysis: {filename}**\n\n"
            summary += f"**Root Element:** {root.tag}\n"
            summary += f"**Root Attributes:** {root.attrib}\n"
            
            # Count child elements
            children = list(root)
            summary += f"**Child Elements:** {len(children)}\n"
            
            if children:
                child_tags = set(child.tag for child in children)
                summary += f"**Child Types:** {', '.join(child_tags)}\n"
            
            # Show structure preview
            summary += f"\n**Structure Preview:**\n```xml\n{xml_content[:1000]}...\n```"
            
            return summary
            
        except ET.ParseError as e:
            return f"Invalid XML file: {str(e)}"
        except Exception as e:
            return f"Error processing XML: {str(e)}"
    
    async def _process_unknown(self, file_data: bytes, filename: str, file_type: str) -> str:
        """Handle unknown file types."""
        try:
            # Try to decode as text
            try:
                text_content = file_data.decode('utf-8', errors='ignore')
                if all(ord(c) < 128 for c in text_content[:100]):  # ASCII check
                    return await self._process_text(file_data, filename)
            except:
                pass
            
            # Binary file analysis
            file_size = len(file_data)
            
            summary = f"📎 **File Analysis: {filename}**\n\n"
            summary += f"**Type:** {file_type}\n"
            summary += f"**Size:** {file_size:,} bytes\n"
            summary += f"**Status:** Binary file (not readable as text)\n\n"
            
            # Show hex preview for small files
            if file_size <= 256:
                hex_preview = ' '.join(f'{b:02x}' for b in file_data[:32])
                summary += f"**Hex Preview:**\n```\n{hex_preview}...\n```"
            
            summary += "\n*This file type is not fully supported for content analysis.*"
            
            return summary
            
        except Exception as e:
            return f"Error analyzing file: {str(e)}"