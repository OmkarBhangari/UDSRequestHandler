## Project Overview
**vanalyzer** is an advanced tool designed to facilitate communication with automotive electronic control units (ECUs) using Unified Diagnostic Services (UDS). The primary purpose of vanalyzer is to enable users to send UDS requests and efficiently handle the responses. It supports the Transport Protocol (TP) for seamless data exchange, ensuring that communication between the tool and the ECU is robust and reliable.

The tool extracts relevant information from the received frames and presents it in a user-friendly tabular format. This clear and organized display allows users to quickly analyze the data, making vanalyzer an essential tool for diagnostics, testing, and development in the automotive domain.

## Installation Guide
- Step-by-step instructions on how to install and set up the app.

## Quick Start
- A simple example or tutorial to help users get up and running quickly.

## Architecture Overview

### Core Classes

#### 1. **Rx and Tx Classes**
- **Purpose**: The most fundamental classes, `Rx` and `Tx`, manage the transmission and reception of messages.
- **Functionality**: These classes interface directly with the hardware using the respective interface, either **PCAN** or **Vector**.

#### 2. **CAN Class**
- **Purpose**: The `CAN` class is responsible for sending and receiving up to 8 bytes of data.
- **Relationship**: Built on top of the `Rx` and `Tx` classes, the `CAN` class utilizes their capabilities for message handling.

#### 3. **CAN_TP Class**
- **Purpose**: Handles data transmission and reception when the data exceeds 8 bytes.
- **Functionality**: All communications pass through the `CAN_TP` class. However, it only takes action when the data size is greater than 8 bytes.

#### 4. **UDS Class**
- **Purpose**: Utilizes the `CAN_TP` class for communication.
- **Services**: The `UDS` class can send various UDS messages (e.g., 0x19, 0x22, 0x2E) to the ECU and receive responses through the `CAN_TP` class.
- **Routing**: It directs the received messages to their respective service classes (`0x19`, `0x22`, `0x2E`).

### UDS Service Classes

#### 1. **0x19, 0x22, 0x2E Service Classes**
- **Purpose**: Each UDS service is divided into separate classes, such as `0x19`, `0x22`, and `0x2E`.
- **Functionality**: These classes contain the logic to handle their respective functionalities.
- **Intelligence**: Each class is designed to intelligently extract and perform analysis on the data received from the `UDS` class.


## Technical Documentation

### Communication Libraries

- **PCANBasic**: The library uses `PCANBasic` for communication with **Peak** hardware. The logic for communicating with **Vector** hardware has not yet been implemented.
  - The `PCANBasic` API has already been included in the project source code, so there is no need to install it using pip.

### GUI and Frontend

- **GUI Framework**: The project uses `pywebview` for the GUI.
- **Frontend Framework**: The frontend is built using `Svelte` as the framework.
- **UI Library**: The `Flowbite` UI library is used for styling and components.

### Initial Setup

1. **Install Node Modules**:
   - Navigate to the `vanalyzer` folder in your terminal:
     ```sh
     cd vanalyzer
     ```
   - Run the following command to install the necessary Node.js modules:
     ```sh
     npm i
     ```

2. **Build and Run the Project**:
   - Return to the root of the project directory:
     ```sh
     cd ..
     ```
   - Run the `r.bat` file:
     ```sh
     ./r.bat
     ```
   - This script will automatically build the frontend, run the Python script that integrates the frontend with the backend, and launch the project.
