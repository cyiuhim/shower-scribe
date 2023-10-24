# Webserver
This folder contains the code for all webserver - related source code.

### Setup Instructions
In the `webserver` folder, run:

```python -m venv venv/```

This will initialize the python virtual environment. 
To enter the virtual environment, run the following command in the repository `webserver`:

```source venv/bin/activate```

To install dependencies, run the following command in the `webserver` folder.

```pip install -r requirements.txt```

### Development
Before installing new dependencies or running code, ensure that the virtual environment is activated (the terminal prompt should be prefixed with `(venv)`). 

To activate the environment, run the following in the repository `webserver`.

```source venv/bin/activate```

Update `requirements.txt` upon installation of any dependencies.
If working across multiple subprojects, make sure the virtual environment is deactivated before working on files outside the `webserver` folder.
The virtual environment can be deactivated using the following:

```deactivate```



