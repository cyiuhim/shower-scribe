# A module for our vector database used for semantic search
import chromadb
chromaClient = chromadb.PersistentClient(path="llm_services/chroma_db")

def add_vector_from_content(text_type,text_id,content):
    # add a vector to the database from the content of a text file
    # text_type is an int, 0 = transcription, 1 = resume, 2 = brainstorm
    # text_id is the id of the text file in the database
    # content is the content of the text file that is then embedded into a vector and stored in the DB
    # returns true if successful, false otherwise
    text_collection = chromaClient.get_or_create_collection("transcriptions")
    try:
        text_collection.add(
            documents=[content],
            metadatas=[{"text_type": text_type}],
            ids=[str(text_id)], 
        )
        return True
    except Exception as e:
        print(e)
        return False

def remove_vector(text_type,text_id):
    # remove a vector from the database
    text_collection = chromaClient.get_or_create_collection("transcriptions")
    count_before = text_collection.count()
    text_collection.delete(
        ids=[text_id],
        where={"text_type": text_type}
    )
    count_after = text_collection.count()
    if count_after < count_before:
        return True
    else:
        return False

def get_n_closest_ids(text_type,content_to_match,n):
    # get the n closest ids to a given text
    # text_type is an int, 0 = transcription, 1 = resume, 2 = brainstorm, or None for all
    # content_to_match is the content of the text file that is then embedded into a vector and compared to the vectors in the DB for the n closest matches
    # n is the number of closest ids to return
    # returns a list of n ids
    text_collection = chromaClient.get_or_create_collection("transcriptions")
    where = None
    if text_type is not None:
        where = {"text_type": text_type}
    query_result = text_collection.query(
        query_texts=[content_to_match],
        n_results=n,
        where=where,
    )
    result_ids = query_result["ids"][0]
    result_ids = [int(i) for i in result_ids] # make them numbers becuase Chroma only takes strings
    return result_ids

def peek_database():
    # print the number of vectors in the database
    print(f"Number of vectors in database: {text_collection.count()}")
    print(f"Peek: {text_collection.peek()}")

def reset_database():
    global text_collection # this line is just really for testing
    # reset the database
    chromaClient.delete_collection("transcriptions")
    text_collection = chromaClient.get_or_create_collection("transcriptions")
