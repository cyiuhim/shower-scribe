from llm_services import cohere_interractions
from webserver.app import app, Recording
import vector_interface

def test():
    with app.app_context():
        # get the transcription from the database
        # transcription = cohere_interractions.get_transcription(1)
        # # print(transcription)
        # assert(transcription!=None)

        # # ask cohere to resume the transcription
        # cohere_response = cohere_interractions.ask_resume_block(transcription)
        # print(cohere_response)

        # # # get the transcription from the database
        # # transcription = cohere_interractions.get_transcription(2)
        # # # print(transcription)
        # # assert(transcription!=None)

        # # # ask cohere to resume the transcription
        # # cohere_response = cohere_interractions.ask_resume_block(transcription)
        # # print(cohere_response)

        # embedding = cohere_interractions.get_semantic_embedding(cohere_response[1])
        # print(embedding)

        vector_interface.reset_database()

        cohere_interractions.full_resume_and_title(1)
        # cohere_interractions.full_resume_and_title(2)
        # cohere_interractions.full_resume_and_title(3)
        # cohere_interractions.full_resume_and_title(4)
        # cohere_interractions.full_resume_and_title(5)


if __name__ == "__main__":
    test()