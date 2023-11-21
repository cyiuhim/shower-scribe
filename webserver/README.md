# Webserver

This folder contains the code for all webserver - related source code.

## Development

Before installing new dependencies or running code, ensure that the virtual environment is activated (the terminal prompt should be prefixed with `(venv)`). 

To activate the environment, run the following in the repository `webserver`.

```source venv/bin/activate```

Update `requirements.txt` upon installation of any dependencies.
If working across multiple subprojects, make sure the virtual environment is deactivated before working on files outside the `webserver` folder.
The virtual environment can be deactivated using the following:

```deactivate```

## Database Setup (that will need to be automated on the PI setup)

Run reset_database.py
