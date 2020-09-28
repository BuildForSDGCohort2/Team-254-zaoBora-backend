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

## Getting Started

### Setting up

================================

Step 1: Click on Fork at the top right corner

Step 3: cd into the cloned folder | cd Team-254-zaoBora-backend

Step 4: ` git remote add upstream <https://github.com/http://127.0.0.1:5000/> `

Step 5: ` git pull upstream develop `

Step 6: Check out to the task branch | ` git checkout -b <NAME_OF_THE_TASK> `

e.g git checkout -b develop/ft-authentication-endpoints

#### Running the project locally (Linux)

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

5. Install
```
$ pip install -r requirements.txt
$ pip freeze > requirements.txt
```

6. Run the app
```
$ python run.py
```

#### Running the project locally (Windows)

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

#### Creating a pull request

Run git branch It should show that you are on your current branch

After implementing your task

Step 1: Run: ` git add . `

Step 2: Run: ` git commit -m "< COMMIT MESSAGE >" `

Step 3: ` git pull upstream develop `

Step 4: ` git push origin < BRANCH_NAME > `

Go to the repository <https://github.com/BuildForSDGCohort2/Team-254-zaoBora-backend>

As soon as you get there, you are going to see a green notification ‘compare and create a pull request’

Click on it, type your message,and click create pull request.

If you have any more questions, please check out this resource  <https://www.youtube.com/watch?v=HbSjyU2vf6Y>

## The following are API endpoints enabling one to

* Create an account and login

### ZaoBora application endpoints

| Endpoint(URLs)                             | Functionality         | HTTP Method    |
|--------------------------------------------|-----------------------|----------------|
| '/users'                                   | Get all users         | GET            |
| '/auth/signup'                             | Register a new user   | POST           |
| '/auth/login'                              | Login a user          | POST           |
| '/auth/<int:userId>/logout'                | Logout a user         | POST           |
| '/profile/<int:userId>'                    | Delete user account   | DELETE         |
| '/profile/<int:userId>'                    | Update user account   | PUT            |
|--------------------------------------------|-----------------------|----------------|
| '/vendors'                                 | Get all vendors       | GET            |
| '/auth/vendor/signup'                      | Register a new vendor | POST           |
| '/auth/vendor/login'                       | Login a vendor        | POST           |
| '/auth/vendor/<int:vendorId>/logout'       | Logout a vendor       | POST           |
| '/profile/vendor/<int:vendorId>'           | Update vendor account | PUT            |
|--------------------------------------------|-----------------------|----------------|
| '/products'                                | Get all products      | GET            |
| '/<int:vendorId>/product'                  | Create a new product  | POST           |
| '/products/<int:productId>'                 | Get a single product  | GET            |
| '/<int:vendorId>/product/<int:productId>'  | Update a product      | GET            |
| '/<int:vendorId>/product/<int:productId>'  | Delete a product      | DELETE         |
|                                            |                       |                |

### Authors

#### Frontend

1. David Macharia (<https://github.com/Dave-mash>)
2. Alexander Thuo (<https://github.com/zanderthuo>)
3. Margret Njeri (<https://github.com/Njeri-Marg>)

#### Backend

1. Derrick Moseti (<https://github.com/moseti1>)
2. Jordan Muthemba (<https://github.com/Jordan-type>)
