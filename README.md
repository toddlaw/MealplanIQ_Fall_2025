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
# Linux / MacOS
python3 -m venv venv

# Windows
python -m venv venv
```

3. Activate the Python environment in the backend directory

```
# Linux / MacOS
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

4. Install dependencies in the backend directory

```
pip install -r requirements.txt
```

5. Install dependencies in the frontend directory

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

1. Make sure the Python environment is activated and run backend server in the backend directory

```
flask run
```

2.  Run the frontend server in the frontend directory

```
ng serve
```

3. Access the application

```
http://localhost:4200/
```
