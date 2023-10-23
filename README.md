# FoodForward

## Team Members

* [Aavishkar Gautam](https://github.com/aavishkar6)
* [Avaneesh Devkota](https://github.com/avaneeshdevkota)
* [Seolin Jung](https://github.com/seolinjung)
* [Soyuj Jung Basnet](https://github.com/basnetsoyuj)

## Product vision statement

*FoodForward* aims to reduce food waste by making surplus food sharing simple, engaging, and accessible for everyone, one meal at a time.

## User stories

* [Issues](https://github.com/software-students-fall2023/2-web-app-exercise-1-sqrt-5-2/issues)

## Task boards

* [Sprint 1](https://github.com/orgs/software-students-fall2023/projects/15/views/1?layout=board)
* [Sprint 2](https://github.com/orgs/software-students-fall2023/projects/35/views/1?layout=board)

## Setup

Copy the `.env.example` file contents to a new `.env` file and edit the details accordingly.

### MongoDB
- Install MongoDB and start the MongoDB server.

### Environment

### Pipenv

To manage dependencies using Pipenv, check [Pipenv](https://pipenv.pypa.io/en/latest/installation/) for details.

Install Pipenv:

```sh
pip install pipenv
```

Install dependencies:

```sh
pipenv install
```

Activate the virtual environment:

```sh
pipenv shell
```

> **Note:** If you are having issues using Pipenv, create virtual environment using venv, activate it and run:
>
> ```
> pip install -r requirements.txt
> ```

Finally, run the flask app using:

```sh
flask run --reload
```

or 

```sh
python app.py
```

### Filler Data

Filler data will be added automatically to the database if there is no data in the collections initially.

Run the following in the root directory if you need to manually add filler data to the database:

```sh
python -m scripts.fill
```

### Default User Accounts

You can log in with one of the following default accounts to easily view the features of the app.

| Email              | Password |
|--------------------|----------|
| furrypig@nyu.edu   | pass1234 |
| alice@gmail.com    | pass1234 |
| bob@nyu.edu        | pass1234 |
| kimberly@gmail.com | pass1234 |
| valencia@gmail.com | pass1234 |
| irene@nyu.edu      | pass1234 |
| harry@nyu.edu      | pass1234 |
| luka@nyu.edu       | pass1234 |
| lara@nyu.edu       | pass1234 |
| michael@nyu.edu    | pass1234 |