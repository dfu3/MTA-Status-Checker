
# MTA Subway Delay Tracker API

This is the API server component for the MTA Subway Delay Tracker. It provides endpoints to fetch real-time delay status and uptime information for specific subway lines based on live GTFS data. The application continuously updates delay data in the background and serves this information via HTTP API endpoints.

---

## Features

- **Real-Time Data Fetching**: Continuously updates subway line delay data
- **API Endpoints**:
  - `/uptime/<line>`: Returns the uptime percentage of a specific subway line.
  - `/status/<line>`: Returns whether a specific subway line is currently delayed.
- **Background Task**: Periodically polls and updates delay information from the MTA's GTFS feed while the server is running.
  - Logs when a Line is newly `delayed` or `recovered`

---

## Configuration

- `POLLING_RATE_SECONDS`: The interval at which the data fetching occurs. Currently set to 10 seconds.
- Change this value to adjust the polling rate
  - Higher rate will be more accurate, but could add noise in the form of quick delays you might not care about
  - Lower rate will be more normalized, but could potentially miss alerts 

---

## Limitations And Considerations

- **Data Availability**:
  - The application relies on the availability and accuracy of GTFS real-time data from the MTA API.
  - If the feed is down or delayed, the data might not be up-to-date.
- **Subway Line Coverage**:
  - The API will only return data for subway lines that are captured by the MTA feed.
  - If a line is not captured in an alert for Delays, the response will indicate it as not delayed, as the __MTA feed is the source of truth__.
- **Data Coupling**:
  - This api is purposly decoupled from any potential caller (there are no shared data states between calls)
  - It is assumed that the caller validates the subways lines supplied to ensure they exist
    - A non-existent line will be returned as _NOT DELAYED_ and with 100% uptime
    - Although this can impact accuracy, it __greatly increases reliabiliy__, which should be priority for a live update service

## Requirements

The script requires the following dependencies:

- Flask==2.3.2
- protobuf==5.29.3
- protobuf3_to_dict==0.1.5
- Requests==2.32.3

To install the dependencies, use:

```bash
pip install requirements.txt
```

---

## Usage

### 1. Run the Script

Start the Flask application along with the polling background task:

```bash
python api.py
```

The application will start a web server and begin polling the MTA GTFS feeds for delay data.

### 2. API Endpoints

- **Uptime Endpoint**:
  
  ```bash
  GET /uptime/<line>
  ```

  Returns the uptime percentage for a specific subway line.
  
  Example Response:

  ```json
  {
    "Line": "A",
    "Uptime": 0.95
  }
  ```

- **Status Endpoint**:
  
  ```bash
  GET /status/<line>
  ```

  Returns the delay status for a specific subway line.

  Example Response:

  ```json
  {
    "Line": "A",
    "Delayed": true
  }
  ```

---



