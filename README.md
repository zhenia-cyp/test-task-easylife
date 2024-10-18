## Test task for the middle python developer position

Admin panel for a referral service


<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/screenshot-easylife.png"/>


## Prerequisites

Before starting the application, ensure you have the following installed:

- Python (version 3.11)
- Pip (version 24.2)

## Installation

1. Clone the repository:
    ```bash
    https://github.com/zhenia-cyp/test-task-easylife.git
    ```

2. Navigate to the project directory:
    ```bash
    cd test-task-easylife
    ```

3. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Unix/Mac
    # or
    .\venv\Scripts\activate   # For Windows
    ```

4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
   
## Running the application

1. To start the application, run the following command:
```bash
python app/main.py
```

## Running the application with docker compose

1. Make sure to configure your environment by creating a .env file with the required variables before running Docker Compose.

To build and start the application using Docker Compose, run the following command:
```bash
docker-compose up --build
```

For subsequent runs, you can use:
```bash
docker-compose up
```

You can access the API endpoints using a web browser.

## Applying migrations with alembic

1. If you haven't already installed Alembic, you can do so using pip:

```bash
pip install alembic
```

2. Before using Alembic, you need to configure it to connect to your database. 
This involves creating an `alembic.ini` file and configuring it with your database connection details:

```bash
sqlalchemy.url = driver://{db_user}:{db_password}@{db_host}/{db_name}
```

3. Run the `alembic revision` command with the `--autogenerate` option to automatically generate migration scripts based on changes in your SQLAlchemy models:

```bash
alembic revision --autogenerate -m "first migration"
```

4. Apply the generated migrations to the database using the alembic upgrade command:

```bash
alembic upgrade head
```
