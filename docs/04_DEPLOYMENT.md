# Deployment

## Deployment Guide

This document provides step-by-step instructions for deploying the "Dark Thoughts" thinking-dataset project. Follow these steps to ensure a smooth deployment process.

## Prerequisites

Before you begin, ensure you have the following:

- **Server/Hosting Environment**: A server or hosting environment with Python 3.7 or higher installed.
- **Database**: SQLite or any other compatible database.
- **Environment Variables**: Necessary environment variables configured for the deployment environment.

## Deployment Steps

### 1. Set Up the Server Environment

1. **Access the Server**: Connect to your server via SSH or any other method provided by your hosting service.

2. **Clone the Repository**: Clone the repository to your server:
   ```bash
   git clone https://github.com/MultiTonic/thinking-dataset.git
   cd thinking-dataset
   ```

3. **Create a Virtual Environment**: Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use .\venv\Scripts\activate
   ```

### 2. Install Dependencies

With the virtual environment activated, install the project and its dependencies:
```bash
pip install -e .
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root directory and configure the necessary environment variables. You can use the provided `.env.example` file as a template:
```bash
cp .env.example .env
```
Edit the `.env` file to include your specific configuration settings.

### 4. Initialize the Database

Run the script to initialize the database:
```bash
python scripts/init_db.py
```

### 5. Configure the Application

Ensure the application is configured correctly by updating any necessary settings in the configuration files. This includes:

- **Database Configuration**: Ensure the database settings in the `.env` file are correct.
- **Server Configuration**: Update any server-specific settings such as host, port, and other configurations.

### 6. Run the Application

Start the application using the following command:
```bash
thinking-dataset
```
Ensure the application is running correctly and accessible from the desired endpoint.

### 7. Set Up Process Manager (Optional)

For production environments, it is recommended to use a process manager such as `pm2` or `supervisord` to ensure the application runs continuously and restarts automatically if it crashes.

#### Using `pm2`
1. **Install pm2**:
   ```bash
   npm install -g pm2
   ```

2. **Start the Application with pm2**:
   ```bash
   pm2 start thinking-dataset
   ```

3. **Save the pm2 Process List**:
   ```bash
   pm2 save
   ```

4. **Set up pm2 Startup Script**:
   ```bash
   pm2 startup
   ```

### 8. Monitoring and Logging

Implement monitoring and logging to keep track of the application’s performance and diagnose any issues. Tools such as `Loguru` (for logging) and various monitoring services can be used.

### 9. Regular Maintenance

Regularly update the project dependencies and environment to ensure the application remains secure and up-to-date:
- **Update Dependencies**:
  ```bash
  pip install --upgrade -r requirements.txt
  ```

- **Pull Latest Changes**:
  ```bash
  git pull origin main
  ```

### 10. Troubleshooting

If you encounter any issues during deployment, refer to the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) file for common issues and their solutions.