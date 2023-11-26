from webserver.app import startup_webserver
from test_llm_interactions import test
import sql_interface

if __name__ == "__main__":
    startup_webserver(debug=True)


