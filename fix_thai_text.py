import re
import sys

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

def fix_thai_file(input_file, output_file):
    """Fix Thai text in a file by removing unnecessary spaces."""
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Clean the text
        cleaned_text = clean_thai_text(text)
        
        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
            
        print(f"Successfully fixed Thai text from '{input_file}' to '{output_file}'")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False
        
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python fix_thai_text.py <input_file> <output_file>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not fix_thai_file(input_file, output_file):
        sys.exit(1) 