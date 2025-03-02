import boto3
import io
from PIL import Image
import tempfile
import os
from config import AWS_REGION

class DocumentProcessingAgent:
    def __init__(self):
        self.textract = boto3.client('textract', region_name=AWS_REGION)
    
    def process_document(self, file):
        """
        Extracts text from a document using AWS Textract.
        
        Args:
            file: The uploaded file object
        
        Returns:
            str: The extracted text
        """
        try:
            # Handle different file types
            file_bytes = file.getvalue()
            
            # For PDF files, we need to convert each page
            if file.name.lower().endswith('.pdf'):
                return self._process_pdf(file_bytes)
            
            # For image files, process directly
            return self._process_image(file_bytes)
            
        except Exception as e:
            return f"Error processing document: {str(e)}"
    
    def _process_image(self, image_bytes):
        """Process an image file with Textract"""
        response = self.textract.detect_document_text(
            Document={'Bytes': image_bytes}
        )
        
        return self._extract_text_from_response(response)
    
    def _process_pdf(self, pdf_bytes):
        """Process a PDF file with Textract"""
        # For simplicity, we'll just process the first page
        # In a production app, you'd process all pages
        
        # Save PDF to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf.write(pdf_bytes)
            temp_pdf_path = temp_pdf.name
        
        try:
            # Start the Textract job
            response = self.textract.start_document_text_detection(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': 'your-s3-bucket',
                        'Name': os.path.basename(temp_pdf_path)
                    }
                }
            )
            
            # In a real application, you would poll for job completion
            # For simplicity, we'll return a placeholder message
            return "PDF processing started. Results will be available soon."
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_pdf_path):
                os.remove(temp_pdf_path)
    
    def _extract_text_from_response(self, response):
        """Extract text from Textract response"""
        text = ""
        for item in response['Blocks']:
            if item['BlockType'] == 'LINE':
                text += item['Text'] + '\n'
        return text 