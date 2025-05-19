#!/usr/bin/env python3
"""
PDF to Text Converter

This script converts PDF files to text files. It can be used to convert a single
PDF file or all PDF files in a directory.

Usage:
    python pdf2txt.py <input_path> [<output_path>] [--fix-thai]

Arguments:
    input_path: Path to a PDF file or directory containing PDF files
    output_path: (Optional) Path to save the text file(s). If not provided,
                text files will be saved in the same location as the PDF files.
                If this is a directory, the text file will be saved in this directory.
    --fix-thai: (Optional) Apply fixes for Thai text extraction issues like extra spacing
"""

import os
import sys
import PyPDF2
import re
from pathlib import Path


def clean_thai_text(text):
    """
    Clean Thai text by removing unnecessary spaces between Thai characters.
    
    Args:
        text (str): The text to clean
        
    Returns:
        str: The cleaned text
    """
    # Define Thai character range in Unicode
    thai_pattern = re.compile(r'[\u0E00-\u0E7F]')
    
    # Replace unnecessary spaces between Thai characters
    cleaned_text = ""
    i = 0
    while i < len(text):
        if i < len(text) - 2 and thai_pattern.match(text[i]) and text[i+1] == ' ' and thai_pattern.match(text[i+2]):
            # Skip the space between Thai characters
            cleaned_text += text[i]
            i += 1  # Skip the current character
        else:
            cleaned_text += text[i]
        i += 1
    
    # Remove duplicate spaces
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    
    return cleaned_text


def convert_pdf_to_text(pdf_path, output_path=None, fix_thai=False):
    """
    Convert a PDF file to a text file.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_path (str, optional): Path to save the text file. If not provided,
                               the text file will be saved in the same location
                               as the PDF file. If this is a directory, the text
                               file will be saved in this directory with the same
                               name as the PDF file.
        fix_thai (bool): Whether to apply fixes for Thai text extraction issues
    
    Returns:
        str: Path to the saved text file
    """
    # Convert paths to Path objects for better cross-platform compatibility
    pdf_path = Path(pdf_path)
    
    # If output_path is not provided, create it based on pdf_path
    if output_path is None:
        output_path = pdf_path.with_suffix('.txt')
    else:
        output_path = Path(output_path)
        
        # If output_path is a directory or doesn't exist
        if output_path.is_dir() or not output_path.exists():
            # Create directory if it doesn't exist
            if not output_path.exists():
                try:
                    output_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    print(f"Error creating directory '{output_path}': {str(e)}")
                    return None
            
            # If it's a directory, add the filename
            if output_path.is_dir() or not output_path.suffix:
                output_path = output_path / f"{pdf_path.stem}.txt"
    
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as file:
            # Create a PDF reader object
            reader = PyPDF2.PdfReader(file)
            
            # Get number of pages
            num_pages = len(reader.pages)
            
            # Extract text from each page
            text = ''
            for page_num in range(num_pages):
                page_text = reader.pages[page_num].extract_text() + '\n'
                if fix_thai:
                    page_text = clean_thai_text(page_text)
                text += page_text
            
            # Create directory for output_path if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write text to file
            with open(output_path, 'w', encoding='utf-8') as txt_file:
                txt_file.write(text)
            
            print(f"Successfully converted '{pdf_path}' to '{output_path}'")
            return str(output_path)
    
    except Exception as e:
        print(f"Error converting '{pdf_path}': {str(e)}")
        return None


def process_directory(dir_path, output_dir=None, fix_thai=False):
    """
    Convert all PDF files in a directory to text files.
    
    Args:
        dir_path (str): Path to the directory containing PDF files
        output_dir (str, optional): Directory to save the text files
        fix_thai (bool): Whether to apply fixes for Thai text extraction issues
    
    Returns:
        list: List of paths to the saved text files
    """
    # Convert paths to Path objects
    dir_path = Path(dir_path)
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    output_files = []
    
    # Process all PDF files in the directory
    for item in os.listdir(dir_path):
        item_path = dir_path / item
        
        # Skip if not a file or not a PDF
        if not item_path.is_file() or not item.lower().endswith('.pdf'):
            continue
        
        # Determine output path
        output_path = None
        if output_dir:
            output_path = output_dir / f"{item_path.stem}.txt"
        
        # Convert PDF to text
        result = convert_pdf_to_text(item_path, output_path, fix_thai)
        if result:
            output_files.append(result)
    
    return output_files


def main():
    # Check if required arguments are provided
    if len(sys.argv) < 2:
        print("Usage: python pdf2txt.py <input_path> [<output_path>] [--fix-thai]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = None
    fix_thai = False
    
    # Parse arguments
    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "--fix-thai":
            fix_thai = True
        elif output_path is None and not sys.argv[i].startswith("--"):
            output_path = sys.argv[i]
    
    # Check if input path exists
    if not os.path.exists(input_path):
        print(f"Error: '{input_path}' does not exist.")
        sys.exit(1)
    
    # Process input based on whether it's a file or directory
    if os.path.isfile(input_path):
        # Process single file
        if not input_path.lower().endswith('.pdf'):
            print(f"Error: '{input_path}' is not a PDF file.")
            sys.exit(1)
        
        convert_pdf_to_text(input_path, output_path, fix_thai)
    else:
        # Process directory
        process_directory(input_path, output_path, fix_thai)


if __name__ == "__main__":
    main()
