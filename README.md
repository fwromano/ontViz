# Ontology Visualization

This project is a Flask web application that loads an ontology (OWL/Turtle) and displays a full‑page, interactive graph (via pyvis) alongside an expandable/collapsible class hierarchy.

## Prerequisites

- Python 3.7 or higher
- Git (optional)

## Setup Instructions

Follow these steps to set up the project:

### 1. Clone the Repository (or Download the Files)

```bash
git clone https://github.com/fwromano/oViz.git
cd oViz
```
### 2. Create and Activate a Virtual Environment

On macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```
On Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

With your virtual environment activated, run:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Start the Flask server by running:

```bash
python app.py
```
Open your browser and go to 

```bash
http://127.0.0.1:5000.
```

### Project Structure
```bash
oViz/
├── app.py               # Main Flask application
├── templates/
│   └── index.html       # HTML template
│   └── uploads.html       # HTML template
├── static/              # Folder for generated files (e.g., graph.html)
├── uploads/             # Folder for uploaded ontology files
└── requirements.txt     # List of required packages
```