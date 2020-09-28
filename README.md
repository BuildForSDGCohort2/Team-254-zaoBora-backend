# Team-254-zaoBora-backend

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1e73c36564264112b181e60608bdfd02)](https://app.codacy.com/gh/BuildForSDGCohort2/Team-254-zaoBora-backend?utm_source=github.com&utm_medium=referral&utm_content=BuildForSDGCohort2/Team-254-zaoBora-backend&utm_campaign=Badge_Grade_Settings)

## Description

Zao Bora is an online platform where people can register and be a part of a community that helps connect farmers with potential retailers and consumers. Through this platform, a hardworking and dedicated farmer can be able to sell and market their produce without the need of a middleman.

## Prerequisites

* Python3
* Git
* Postmam
* Redis
* PostgreSQL
* python3-venv

## Project setup (Linux)

================================

1. Clone repo
```
$ git clone https://github.com/BuildForSDGCohort2/Team-254-zaoBora-backend.git
```

2. On your terminal, install python3-venv (skip this step if you already have python3-venv)
```
$ sudo apt-get install python3-venv
```

3. Cd into project directory and create virtual environment
```
$ python -m pip install --upgrade pip
$ cd Team-254-zaoBora-backend
$ python3 -m venv env
```

4. Set the environment variables and create db
- Create an instance folder in the root of the project, inside create a `__init__.py` and a `config.py` and copy these contents -> [Contents](https://gist.github.com/Dave-mash/c0853979343257db52dd251ed4c54219) into `config.py`
```
$ mv .env.example .env
$ source env/bin/activate
$ source .env
$ createdb zaobora_database
```

5. Install dependencies
```
$ pip install -r requirements.txt
$ pip freeze > requirements.txt
```

6. Run the app
```
$ python run.py
```

## Project setup (Windows)

================================

1. Clone repo
```
$ git clone https://github.com/BuildForSDGCohort2/Team-254-zaoBora-backend.git
```

2. Cd into project directory and create virtual environment
```
$ py -m pip install --upgrade pip
$ cd Team-254-zaoBora-backend
$ py -m venv env
```

4. Set the environment variables and create db
- Rename .env.example to .env
- Create an instance folder in the root of the project, inside create a `__init__.py` and a `config.py` and copy these contents -> [Contents](https://gist.github.com/Dave-mash/c0853979343257db52dd251ed4c54219) into `config.py`
```
$ .\env\Scripts\activate
```
- Login to postgres shell and run:
```
$ CREATE DATABASE zaobora_database;
```

5. Install
```
$ pip install -r requirements.txt
$ pip freeze > requirements.txt
```

6. Run the app
```
$ python run.py
```

## Authors

1. [Derrick Moseti](<https://github.com/moseti1>)
2. [Jordan Muthemba](<https://github.com/Jordan-type>)
3. [David Macharia](<https://github.com/Dave-mash>)
