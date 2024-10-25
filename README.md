# MealPlanIQ_May_2024

## Required

1. Python 3.11+
2. Node 20+

## Installation

1. Clone repository

```
git clone https://github.com/toddlaw/MealPlanIQ_May_2024.git
```

2. Create a Python virtual environment in the backend directory to store dependencies

```
# go to backend folder
cd backend
```

```
# Linux / MacOS
python3 -m venv venv

# Windows
python -m venv venv
```

3. Activate the Python environment in the backend directory

```
# Linux / MacOS
source venv/bin/activate

# Windows powershell
.\venv\Scripts\activate
```

```
# Windows Gitbash
source venv/scripts/activate
```

4. Install dependencies in the backend directory

```
pip install -r requirements.txt
```

```
pip install cryptography
```

5. Install dependencies in the frontend directory

```
# go to frontend folder
cd frontend
```

```
npm install --force
```

6. Install Angular CLI to run ng commands

```
npm install -g @angular/cli
```

7. Create a folder called environments under the **frontend/src** directory
8. Place the environment.ts and environment.prod.ts files in the newly created environments folder (Files to be provided by the owner)
9. Place the .env file under the **backend** directory (Files to be provided by the owner)

## Usage

1. Make sure the database is connected

   1.1 Download the sql file (the file to be provided by the owner)

   1.2 Rename the file to avoid white space in the name

   1.3 Upload the database file into your local databse

   Open command prompt and run

   ```
   mysql -u <username of your database connection> -p -t < <the file name with extension>
   ```

   1.4 Change the "password" variable in the .env to your database account password

2. Make sure the Python environment is activated and run backend server in the backend directory

```
flask run
```

3.  Run the frontend server in the frontend directory

```
ng serve
```

4. Access the application

```
http://localhost:4200/
```
