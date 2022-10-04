# OpenPVSignal editor

OpenPVSignal is an ontology aiming to foster the publication of Pharmacovigilance Signal information, which is currently communicated by drug regulatory authorities via their Newsletters or Web sites as free-text reports.

OpenPVSignal editor consists of two applications:

1. The backend services, implementing the various functionalities (e.g. edit, save, remove), provided by the editor to the user
2. The frontend which allows the user to utilize the available backend services 


## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install on your system

For OpenPVSignalDAL application, you have to install

```
* Python 3.x.x
* flask via pip
* itsdangerous via pip
* rdflib via pip
* SPARQLWrapper via pip
```

For OpenPVSignalFrontend application, you have to install

```
* Python 3.x.x
* flask via pip
* flask-WTF via pip
* itsdangerous via pip
* requests via pip
```

Alternatively, you can install the requirement packages found in the respective requirements.txt file for each application via pip.


## Deployment

Adjust settings in the config.py file found in the directory of each application (OpenPVSignalDAL, OpenPVSingalFrontend) to your own system settings.

* Just run app.py in the local directory with python3 on your local machine **for development and testing purposes**.
* To deploy the project **on a live system**, follow the instruction given by the official documentation of flask on http://flask.pocoo.org/docs/0.12/deploying/ 

## Built With

* [Python 3.8.13](http://www.python.org/) - Developing with the best programming language
* [Flask 2.2.2](http://flask.pocoo.org/) - Flask web development, one drop at a time

## Authors

* **Vlasios Dimitriadis** - *Initial work* - [openpvsignal-editor](https://github.com/bdimitriadis/openpvsignal-editor.git)



