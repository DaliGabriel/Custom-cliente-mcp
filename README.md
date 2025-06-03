# Weather Service Application

A simple weather service that retrieves current weather information using the National Weather Service API.

## Prerequisites

- Python 3.10+
- uv package manager
- Virtual environment (automatically created in setup)

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DaliGabriel/Custom-cliente-mcp.git
   cd mcp-client
   ```

2. Set up the virtual environment and install dependencies:
   ```bash
   uv venv
   ```

## Running the Application

The application consists of two main components that need to run in separate terminals.

### Terminal 1: Start the Server

1. Navigate to the project directory and activate the virtual environment:
   ```bash
   cd .\mcp-client\
   .\.venv\Scripts\activate
   ```

2. Start the server:
   ```bash
   uv run .\server.py
   ```
   Keep this terminal window open and running.

### Terminal 2: Run the Client

1. Open a new terminal window
2. Navigate to the project directory and activate the virtual environment:
   ```bash
   cd .\mcp-client\
   .\.venv\Scripts\activate
   ```

3. Run the client with the server file:
   ```bash
   uv run .\client.py .\server.py
   ```

## Example Usage

Once both server and client are running, you can ask for weather information by providing latitude and longitude coordinates. For example:

```
What's the weather at this location? (latitude: 40.7128, longitude: -74.0060)
```

This will return the current weather conditions for New York City.

## API Reference

This application uses the National Weather Service API for weather data.