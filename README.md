# Ontology Visualization

This project is a Flask web application that loads an ontology (OWL/Turtle) and displays an interactive, full‑page graph (powered by pyvis) alongside an expandable/collapsible class hierarchy. In addition, users can filter nodes and edges, perform text searches, and toggle detailed annotations—all from an adjustable sidebar.

## Features
- Interactive Graph View: Explore the ontology via a dynamic graph that supports zooming, panning, and resetting the view.
- Class Hierarchy: Browse an expandable/collapsible tree of classes.
- Sidebar Controls:
    - Node Filters: Toggle which node types (classes, properties, individuals) are visible.
    - Edge Filters: Select which relationship types (subclass, instance, domain, range) to display.
    - Search: Quickly locate nodes via a text search.
    - Detailed Annotations: Option to show basic info by default or expand to view all available metadata.
    - Resizable & Collapsible Sidebar: Adjust the sidebar’s width or collapse/reopen it using the provided controls.

## Prerequisites

- Python 3.7 or higher
- Git (optional)

## Setup Instructions

Follow these steps to set up the project:

### 1. Clone the Repository (or Download the Files)

```bash
git clone https://github.com/fwromano/ontViz.git
cd ontViz
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
http://127.0.0.1:5000
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