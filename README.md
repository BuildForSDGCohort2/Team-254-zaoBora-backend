# Team-254-zaoBora-backend

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/1e73c36564264112b181e60608bdfd02)](https://app.codacy.com/gh/BuildForSDGCohort2/Team-254-zaoBora-backend?utm_source=github.com&utm_medium=referral&utm_content=BuildForSDGCohort2/Team-254-zaoBora-backend&utm_campaign=Badge_Grade_Settings)

## Description

Zao Bora is an online platform where people can register and be a part of a community that helps connect farmers with potential retailers and consumers. Through this platform, a hardworking and dedicated farmer can be able to sell and market their produce without the need of a middleman.

## Prerequisites

* Python3
* Git
* Postmam
* PostgreSQL

## Getting Started

### Setting up

Step 1: Click on Fork at the top right corner

Step 3: cd into the cloned folder | cd Team-254-zaoBora-backend

Step 4: git remote add upstream <https://github.com/http://127.0.0.1:5000/>

Step 5: git pull upstream develop

Step 6: Check out to the task branch | git checkout -b <NAME_OF_THE_TASK>

e.g git checkout -b develop/ft-authentication-endpoints

#### Running the project locally

Step 1: cd to the cloned folder on termimal type py -m venv env or python -m venv env to install the virtual enviroment

Step 2: Install pip install -r requirements

Step 3: Setup a PostgreSQL Database on config.py

Step 4: Run python -m flask run to test your database connection

Step 4: Go to <http://localhost:5000> or <http://127.0.0.1:5000>

#### Creating a pull request

Run git branch It should show that you are on your current branch

After implementing your task

Step 1: Run: git add .

Step 2: Run: git commit -m "< COMMIT MESSAGE >"

Step 3: git pull upstream develop

Step 4: git push origin < BRANCH_NAME >

Go to the repository <https://github.com/BuildForSDGCohort2/Team-254-zaoBora-backend>

As soon as you get there, you are going to see a green notification ‘compare and create a pull request’

Click on it, type your message,and click create pull request.

If you have any more questions, please check out this resource  <https://www.youtube.com/watch?v=HbSjyU2vf6Y>

## The following are API endpoints enabling one to

* Create an account and login

### ZaoBora application endpoints

| Endpoint(URLs)              | Functionality       | HTTP Method |
|-----------------------------|---------------------|-------------|
| '/auth/register'            | Register a user     | POST        |
| '/auth/login'               | Login a user        | POST        |
| '/auth/<int:userId>/logout' | Logout a user       | POST        |
| '/profile/<int:userId>'     | Delete user account | DELETE      |
|                             |                     |             |
|                             |                     |             |
|-----------------------------------------------------------------|

### Authors

#### Frontend

David Macharia (<https://github.com/Dave-mash>)
Alexander Thuo (<https://github.com/zanderthuo>)
Margret Njeri (<https://github.com/Njeri-Marg>)

#### Backend

Derrick Moseti (<https://github.com/moseti1>)
Jordan Muthemba (<https://github.com/Jordan-type>)
