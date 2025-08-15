# Dockerized Stock Market Data Pipeline with Airflow

This project implements a Dockerized data pipeline using Apache Airflow to automatically fetch, parse, and store daily stock market data from the Alpha Vantage API into a PostgreSQL database.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Running the Pipeline](#running-the-pipeline)
- [Accessing Airflow UI](#accessing-airflow-ui)
- [Verifying the Data](#verifying-the-data)
- [Stopping the Pipeline](#stopping-the-pipeline)
- [Improvements Implemented](#improvements-implemented)

## Features
- **Automated Data Fetching**: Scheduled daily jobs to retrieve the latest stock data.
- **Dockerized Environment**: All services (Airflow, PostgreSQL) are containerized for easy setup and deployment.
- **Robust Error Handling**: The pipeline is designed to handle API errors and network issues gracefully.
- **Secure Credential Management**: API keys and database passwords are managed securely using environment variables.
- **Idempotent Writes**: Uses `INSERT ... ON CONFLICT` to prevent duplicate data entries, making tasks safe to re-run.
- **PythonOperator**: Uses the best-practice `PythonOperator` to run Python logic directly.
- **Email Alerts**: Automatically sends an email notification if a pipeline task fails.

## Architecture
The pipeline consists of the following Docker containers:
1.  **`airflow-webserver`**: The Airflow UI to monitor and manage DAGs.
2.  **`airflow-scheduler`**: The Airflow component that schedules and triggers tasks.
3.  **`airflow-init`**: A one-time service that initializes the Airflow database.
4.  **`postgres-airflow`**: A PostgreSQL database that serves as the backend for Airflow to store its metadata.
5.  **`postgres-stock-data`**: A separate PostgreSQL database to store the fetched stock market data.

## Prerequisites
- **Docker Desktop**: [Install Docker](https://docs.docker.com/get-docker/)
- **An Alpha Vantage API Key**: Get a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

## Setup and Installation
1.  **Clone the repository or place all files in a single directory.**
    The project should have the following structure:
    ```
    .
    ├── dags/
    │   └── stock_market_dag.py
    ├── scripts/
    │   └── fetch_and_store.py
    ├── docker-compose.yml
    └── README.md
    ```

2.  **Create an environment file for your API key:**
    Create a file named `.env` in the root directory of the project and add your Alpha Vantage API key to it:
    ```
    ALPHA_VANTAGE_API_KEY=YOUR_API_KEY_HERE
    ```

3.  **(Optional) Configure Email Alerts:**
    To test email alerts, open the `docker-compose.yml` file and replace the placeholder `AIRFLOW__SMTP__*` variables with your own email provider's credentials (e.g., a Gmail address and an App Password).

## Running the Pipeline
1.  **Build and Run the Containers:**
    Open a terminal in the project's root directory and run:
    ```bash
    docker-compose up -d --build
    ```
    This command will download all necessary images, build the services, and start them in the background. Please wait 1-2 minutes for all services to initialize.

## Accessing Airflow UI
1.  Open your web browser and navigate to `http://localhost:8080`.
2.  Log in with the default credentials automatically created by the system:
    - **Username**: `admin`
    - **Password**: `admin`
3.  On the main dashboard, find the `stock_market_data_pipeline` DAG. Enable it by clicking the toggle on the left, then trigger it manually by clicking the "play" button on the right.

## Verifying the Data
After a successful DAG run, you can connect to the stock data PostgreSQL database to verify that the data has been inserted correctly.
```bash
docker-compose exec postgres-stock-data psql -U stockuser -d stockdata -c "SELECT * FROM stock_data LIMIT 10;"

Stopping the Pipeline
To stop and remove all the containers, networks, and volumes, run:

docker-compose down --volumes

Improvements Implemented
PythonOperator: The core data fetching logic is executed using the PythonOperator for better integration with Airflow.

Email on Failure: The pipeline is configured to send an email alert to a specified address if any task fails, allowing for proactive monitoring.

</markdown>
