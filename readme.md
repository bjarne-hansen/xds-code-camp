# README

This project contains packages and modules for an IHE XDS Code Camp accessing IHE XDS Services ITI-18, ITI- 41, and
ITI-43 using Python.

Specifically, the project also contains utility code for handling special WS-Security, SAML, and XML-DSIG elements
required to access IHE XDS services in a Danish context.

## Getting Started

Clone the source from the GitHub repository:

```
>git clone https://github.com/bjarne-hansen/xds-code-camp 
```

Create virtual environment in the source directory:

```
>virtualenv venv
```

Install requirements using pip:

```
>pip install -r requirements.txt
```
    
Set python path and flask app:

```
>export PYTHON_PATH=./src
>export FLASK_APP=./examples/simple_server.py
```
    
You should now be ready to consult the slides for the code camp and run the examples included in the `./examples`
directory of the project.

The slides can be found in `./doc/XDS Code Camp Slides.pdf`.

Several standards, profiles, and specifications referred to in the slides are also provided for reference in the
`./doc` directory. Newer versions should be downloaded if required. Links are found at the end of the slides.


