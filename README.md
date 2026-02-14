# AI-SOC Lite: AI-Driven Behavioral Security Operations Platform

This repository contains the code for an AI-powered lightweight Security Operations Platform (AI-SOC Lite) designed for Small and Medium Businesses (SMBs). It focuses on behavioral anomaly detection, intelligent risk scoring, and AI-generated, plain-language incident reports.

## Project Structure

This project is organized into three main components:

-   **`backend/`**: Contains the FastAPI application, which serves as the central processing unit.
    -   Log Ingestion, Feature Engineering, AI-Based Anomaly Detection, Rule-Based Detection, Risk Scoring, and LLM-Based Incident Report Generation.
    -   Uses SQLAlchemy with SQLite for persistent data storage.
-   **`frontend/`**: Contains the React application, providing a user-friendly dashboard.
    -   Displays real-time alerts, risk heatmaps, anomaly lists, and allows manual log ingestion and model training.
    -   Communicates with the FastAPI backend.
-   **`agent/`**: Contains a Python-based agent designed to run on customer Windows machines.
    -   Collects logs from Windows Event Logs (Security, System, Application).
    -   Forwards collected logs to the FastAPI backend for analysis.

## Setup and Running the Project

To get the AI-SOC Lite system up and running, follow these steps. You will need **three separate terminal windows/tabs** for the backend, frontend, and agent/log generator.

### Prerequisites

*   **Python 3.9+:** (backend, agent) Ensure Python is installed and added to your system's PATH.
*   **Node.js & npm:** (frontend) Ensure Node.js (which includes npm) is installed.
*   **Git:** For cloning the repository.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-soc-lite-repo
```

### 2. Set Up the Backend

Navigate to the `backend` directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 3. Set Up the Frontend

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

### 4. Set Up the Agent (Windows Machine)

The agent is designed to run on a Windows machine. You will need to copy the `agent/` folder to your Windows machine to build and run it.

**On your Windows Machine:**
*   Ensure **Python 3.9+** is installed and added to PATH.
*   Open a **Command Prompt (Admin)** or **PowerShell (Admin)**.
*   Navigate to your agent directory (e.g., `cd C:\path	o\ai-soc-lite-repo\agent`).
*   Install agent dependencies:
    ```cmd
    pip install -r requirements.txt
    ```
    *(Note: `python-wmi` will pull in `pywin32`.)*

### 5. Run the Components (Simultaneously)

You will need **three separate terminal windows/tabs** open to run the backend, frontend, and then to either run the agent or generate sample logs.

#### **Terminal 1: Start FastAPI Backend**

1.  Open a new terminal.
2.  Navigate to the backend directory:
    ```bash
    cd ai-soc-lite-repo/backend
    ```
3.  Start the FastAPI server (in the foreground for visibility):
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8000
    ```
    *   **Wait until you see:** `INFO: Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)`.
    *   Leave this terminal open.

#### **Terminal 2: Start React Frontend**

1.  Open a second new terminal.
2.  Navigate to the frontend directory:
    ```bash
    cd ai-soc-lite-repo/frontend
    ```
3.  Start the React development server:
    ```bash
    npm run dev
    ```
    *   **Wait until you see:** `➜ Local: http://localhost:5173/`.
    *   Leave this terminal open.

#### **Terminal 3: Ingest Logs (Choose ONE option)**

**Option A: Run the Sample Log Generator (from your Linux machine)**

This script will send pre-defined "normal" and "anomalous" logs to your backend and trigger model training.

1.  Open a third new terminal.
2.  Navigate to the backend directory:
    ```bash
    cd ai-soc-lite-repo/backend
    ```
3.  Run the log generation script:
    ```bash
    python log_generator.py
    ```
    *   Observe logs being processed in Terminal 1.

**Option B: Run the Windows Agent (from your Windows machine)**

This will make your Windows machine send its actual Event Logs to the backend.

1.  **On your Windows Machine:**
    *   Open a **Command Prompt (Admin)** or **PowerShell (Admin)**.
    *   Navigate to your agent directory: `cd C:\path	o\ai-soc-lite-repo\agent`
    *   **Important:** Edit `agent.py` and set `FASTAPI_URL` to `http://<IP_OF_YOUR_LINUX_MACHINE>:8000` (replace `<IP_OF_YOUR_LINUX_MACHINE>` with the actual IP address of the machine running the FastAPI backend).
    *   Run the agent:
        ```cmd
        python agent.py
        ```
    *   Observe logs being processed in Terminal 1 (on your Linux machine).

### 6. Access the Dashboard

*   Open your web browser and go to `http://localhost:5173/` (if frontend is running locally).
*   You should now see the AI-SOC Lite dashboard populated with summary data and detected anomalies. You can interact with the "Generate Report" buttons.

### Deployment to Cloud (Future Consideration)

For a fully "industry-ready" solution, you would deploy the `backend` and `frontend` to cloud hosting platforms (e.g., Render for backend, Vercel for frontend). You would then configure `FASTAPI_URL` in both the agent and the frontend to point to your deployed backend's public URL. Refer to the previous discussions on preparing for cloud deployment if you wish to proceed with this.
