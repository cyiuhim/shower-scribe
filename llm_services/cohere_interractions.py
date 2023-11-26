import os
from dotenv import load_dotenv
import cohere
import bleach
import uuid
import sql_interface
import filesystem_interface
import vector_interface

# This service will take in transcription ids, and then query cohere for data, store it in a new textfile, and add it to the database
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
dotenv_path = os.path.join(parent_dir, '.env')
load_dotenv(dotenv_path)

co = cohere.Client(os.environ["COHERE_API_KEY"])

def get_transcription(text_id: int) -> str|None:
    """Takes in a text id, and returns the transcription's content as a string, or None if it fails."""
    # get transcription from database
    if text_id is None:
        print("None is not a valid text id")
        return None
    
    # transcription = TextFile.query.get(ident=text_id)
    transcription = sql_interface.get_text_as_dict(text_id)
    if transcription is None:
        # print(f"Error getting transcription with id {text_id}, there is probably no transcription for this recording")
        return None
    
    # check the type, if its not a transcription type, return None
    if transcription["type"] != 0:
        print(f"Text with id {text_id} is not a transcription")
        return None
    
    # get the content of the text file
    # the path for the recording is based off the path of the webserver app, so we need to get that
    try:
        transcription_content = filesystem_interface.get_text_content(transcription['text_filename'])
        return transcription_content
    except:
        print(f"Error opening transcription file {transcription['text_filename']}")
        return None
    
    

def ask_resume_block(content:str) -> tuple[str,str]|None:
    """Ask cohere to resume a transcription block. Returns the response from cohere as a touple split into the title and the resume. Will only attempt once. If it fails, returns None."""
    prompt = f"Resume the following transcription in up to two sentences with a title up to 6 words, from the perspective of the author. Give the output in the format 'Title: ..... newline Resume: ....'.\n\n{content}\n"
    try:
      response = co.generate(
        prompt=prompt,
        model='command',
        max_tokens=1000,
        temperature=0.7,
      )
    except cohere.CohereAPIError:
      print(f"Failed to query cohere API.")
      return None

    text = response.generations[0].text

    # html sanitization
    text = bleach.clean(text, tags=[], strip=True)

    # check that the response has the parts we need and isnt an AI error message like "I cant do that"
    if "Title:" not in text or "Resume:" not in text:
        print(f"Error: AI returned a response without a title or resume.")
        return None
    
    # split the text into the title and the resume
    resume_index = text.index("Resume:")

    title = text[:resume_index]
    resume = text[resume_index:]

    # remove the "Title:" and "Resume:" parts
    title = title.replace("Title:", "")
    resume = resume.replace("Resume:", "")

    # strip and remove newlines
    title = title.replace("\n", " ").strip().replace("  ", " ")
    resume = resume.replace("\n", " ").strip().replace("  ", " ")

    return title, resume

def save_text(filename:str,display_name:str,content:str,type:int,associated_recording_id:int) -> int|None:
    """Save a text file to the database. Returns the id of the new text file, or none if it failed to save."""
    # save the text file to the userdata folder
    file_save_answer = filesystem_interface.set_text_content_filename(filename,content)
    if not file_save_answer:
        return None
    
    # create a new text file object
    t = {}
    t["text_filename"] = filename
    t["display_name"] = display_name
    t["type"] = type
    t["associated_recording_id"] = associated_recording_id

    # add it to the database
    created_id = sql_interface.create_text_from_dict(t)

    # return the id
    return created_id

def save_resume(recording_id:int,display_name:str,content:str) -> int|None:
    """Does all the work to save a resume to the database, including linked opperations like updating the associated resume for a recording. Returns the id of the new text file, or none if it failed to save."""
    recording = sql_interface.get_recording_as_dict(recording_id)
    if recording is None:
        print(f"Error getting recording with id {recording_id}")
        return None

    resume_filename = f"resume_{uuid.uuid4()}.txt"
    resume_display_name = f"Resume for {display_name}"
    text_id =  save_text(resume_filename,resume_display_name,content,1,recording_id)

    # add the text id to the recording
    sql_interface.update_recording_associated_resume(recording_id,text_id)
    sql_interface.update_recording_flag_resumed(recording_id)

    return text_id

def save_title(recording_id:int,title:str) -> bool:
    """Saves the title in the database. Returns True if successful, False if not."""
    return sql_interface.update_recording_display_name(recording_id,title)

def add_resume_to_embedding(content:str,text_id:int) -> None:
    """Adds the resume to the semantic embedding. Returns nothing."""
    vector_interface.add_vector_from_content(1,text_id,content)

def full_resume_and_title(recording_id:int) -> int|None:
    """Get the full resume and title for a recording id. Calling an external API so might be quite slow to run, may be blocking. Returns the new resume's text.id if successful, None if it fails in any way."""
    print(f"Recording id: {recording_id}")
    # get the recording
    recording = sql_interface.get_recording_as_dict(recording_id)
    if recording is None:
        print(f"Error getting recording with id {recording_id}")
        return None
    
    # check that the recording has not already been resumed
    if recording["flag_resumed"]:
        print(f"Recording with id {recording_id} has already been resumed")
        return None
    
    # check that the recording has a transcription
    if not recording["flag_transcribed"]:
        print(f"Recording with id {recording_id} has not been transcribed yet, cannot resume")
        return None
    
    # get the transcription
    transcription = get_transcription(recording["associated_transcription_id"]) # for the momenet this isnt implemented, so we'll fake it
    if transcription is None:
        print(f"Error getting transcription for recording with id {recording_id}")
        return None
    
    # get the resume and title, this should try three times
    response = ask_resume_block(transcription)
    if response is None:
        print(f"Error getting resume for recording with id {recording_id}")
        return None
    
    title, resume = response
    
    # save the title and resume
    save_title_answer = save_title(recording_id,title) # this saves the title to the recording
    resume_id = save_resume(recording_id,title,resume)
    if not save_title_answer or resume_id is None:
        print(f"Error saving title or resume for recording with id {recording_id}, {save_title_answer}, {resume_id}")
        return None

    add_resume_to_embedding(resume,resume_id)

    return resume_id
