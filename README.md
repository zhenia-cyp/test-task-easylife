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

## How to use

To test the referral system, follow these steps:

### User Registration

Register three users.
The first user (User 1) will make the second user (User 2) their referral, 
and the second user (User 2) will make the third user (User 3) their referral.
For the first user, the others will be referrals of the first and second line.

The referrer will receive 10% of the amount specified in the transaction from 
the first line, and 5% from the second line.

### test data

```
 {
  "username": "Artem",
  "email": "artem@gmail.com",
  "password": "artem123",
  "password_check": "artem123"
}
```
```
User: id: 1, username: Artem, email: artem@gmail.com, referral_code: 6c317a9e-d
```
```
{
  "username": "Billy",
  "email": "boris@gmail.com",
  "password": "boris123",
  "password_check": "boris123"
}
```
```
User: id: 2, username: Billy, email: boris@gmail.com,referral_code: 2957fd4b-1
```
```
{
  "username": "Vlad",
  "email": "vlad@gmail.com",
  "password": "vlad123",
  "password_check": "vlad123"
}

```
```
 User: id: 3, username: Vlad, email: vlad@gmail.com,referral_code: ddbad83e-8
```

Each user gets a unique code when they register, which is used to connect the referrer and their referral.

### Create the referral

In the database, there is a table called Referral, which tracks the relationship between a user and their referral.

referrer_id – the one who invites.
referred_id – the one who was invited, i.e., the referral.

To create a new referral, we need the referrer's unique code. In our case, that's the unique code 6c317a9e-d for user Artem. 
We also need the ID of the future user who will be the referral, which is Billy with ID: 2.

<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/screenshot%20endpoint1.png"/>
<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/screenshot%20response.png"/>

So, we have created a first-level referral for the user with ID: 1.
Now, to create a second-level referral, User ID 2 (Billy) needs to make User ID 3 (Vlad) their referral.

<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/endpoint2.png"/>
<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/response2.png"/>

### Let’s get some bonuses!

To receive commissions from first (10%) and second-level (5%) referrals, those users need to make purchases.

Creating transactions:

<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/screenshot%20transac%201.png"/>

<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/screenshot%20trac%202.png"/>

So, the referrals made purchases totaling 770 usd and 1000 usd. 
Let’s go to the admin panel and check the earnings.

<img src="https://github.com/zhenia-cyp/images-for-readme-files/blob/main/screenshots/admin1.png"/>

I have also implemented the ability to withdraw funds from the user’s balance, filter transactions by date, 
view a list of your referrals, and see those who haven’t joined yet.









