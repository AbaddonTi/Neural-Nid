

# Neuronal-Nid Project

Demo Reel : ```https://drive.google.com/file/d/1XOzLi-MXFg9R_dqyCqucIAb_voxPManr/view?usp=sharing```


## Project Structure

```
.
├── backend
│   ├── Backend.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend
│   ├── Dockerfile
│   └── static
│       ├── index.html
│       ├── manifest.json
│       ├── script.js
│       └── style.css
├── logs
│   └── logs.csv
├── statistics
│   ├── Dockerfile
│   ├── Statistics.py
│   └── requirements.txt
└── update.sh
```


## Project Overview

The **Neural-Nid** project is a comprehensive system comprising backend and statistics components built with FastAPI, a frontend interface, and logging functionality. The key components are containerized using Docker for streamlined deployment and communication.

### Backend
- **Backend.py**: Handles requests from the frontend, processes data, and returns responses. It also sends duplicate data to the statistics component.
- **Dockerfile**: Defines the Docker image for the backend service.
- **requirements.txt**: Lists the dependencies required by the backend.

### Frontend
- **Dockerfile**: Defines the Docker image for the frontend service.
- **static/**: Contains static files including `index.html`, `manifest.json`, `script.js`, and `style.css`.

### Logs
- **logs.csv**: Stores the collated data from the backend and statistics services.

### Statistics
- **Statistics.py**: Receives data from the backend, collates it into a CSV file stored in the `logs` directory.
- **Dockerfile**: Defines the Docker image for the statistics service.
- **requirements.txt**: Lists the dependencies required by the statistics service.

### Additional Components
- **update.sh**: Script for updating and deploying the entire system on the server.
- **backup/**: Stores essential files for emergency system recovery.

## Functionality

- The **backend** component, built with FastAPI, processes and responds to requests from the frontend and forwards a copy of the data to the **statistics** component.
- The **statistics** component, also built with FastAPI, compiles received data into a CSV file located in the `logs` directory.
- An independent Google Sheets script requests the CSV file from the server every minute, updating the spreadsheet with the latest data.
- All components are deployed in Docker containers, facilitating communication within a Docker network.

## Deployment

To deploy the entire service, clone the repository and run the `update.sh` script from the root directory:

```bash
git clone git@github.com:AbaddonTi/Neural-Nid.git
chmod +x /root/Neural-Nid/update.sh && /root/Neural-Nid/update.sh
```
