# A module that handles file system interactions (notably getting and saving text files, 
# and getting the paths for a recording based off the id.)
# Also does environment variable loading

from dotenv import load_dotenv
import os

# Environment variables and settings
load_dotenv('.env')

#print(f'To test the varaibles got imported at all: {os.getenv("COHERE_API_KEY")}')

# Text file methods
        
def get_text_content(text_filename):
    """Get the content of a text file. Returns None if the file does not exist. Filename must include .txt, but not the path"""
    try:
        with open(f"webserver/userdata/texts/{text_filename}", "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error getting text file {text_filename}, {e}")
        return None

        
def set_text_content_filename(text_filename,content):
    """Set the content of a text file. Returns true if successful, false otherwise. Filename must include .txt, but not the path"""
    try:
        with open(f"webserver/userdata/texts/{text_filename}", "w") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error settig file {text_filename}, {e}")
        return False