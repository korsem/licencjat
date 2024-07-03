## Requirements 
* Python 
* Django 
* Django Rest framework
* PostgreSQL

## Installation
1) Clone the repository 
```
git clone
```
2) Make sure you have Python installed
If not got to https://www.python.org/downloads/ and download Python 3.10 or Python 3.11.

3) Enter the folder with repository and create a virtual environment

* for Linux:
    ```
    python -m venv .venv
    ```
* for Windows:
    ```
    py -m venv .venv 
    ```
  
4) Activate the virtual environment
* for Linux:
    ```
    source .venv/bin/activate
    ```
* for Windows:
    ```
    .venv\Scripts\activate 
    ```
    <sup>When facing <code>cannot be loaded because running scripts is disabled on this system.</code> message, type 
<code>Set-ExecutionPolicy Unrestricted -Scope Proces</code> in PowerShell.</sup>
    <sup>For more info, visit: [Virtualenv won't activate on Windows](https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows).</sup>


5) If you are using Pycharm go to: 
    `File -> Settings -> Project -> Python Interpreter -> Add Interpreter -> virtualenv environment -> Existing environment -> Interpreter -> choose the path to the venv folder that you've created.`

6) Install the latest version of pip
    ```
    python -m pip install --upgrade pip
    ```

7) Install all the required dependencies
    ```
    pip install -r requirements.txt
    ```
   

## Launching the database

1) Configure the database settings in 'settings.py'
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_database_password',
        'HOST': 'your_host',
        'PORT': 'your_port',
    }
}
```
Where in "your ..." write the data for your database
you can do it by creating '.env' file (recommended) like this:
```
touch .env
```
to create .env file
Then fill your .env file like this:
```
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_database_password
DB_HOST=your_host
DB_PORT=your_port
```
2) Perform database migrations
```
python manage.py migrate
```
## Starting the server
1) Run server by
```
python manage.py runserver
```
2) Open the app
```
http://127.0.0.1:8000/
```