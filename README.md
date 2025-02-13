# Ontology Visualization

OntViz is a powerful Flask web application that lets you upload and explore ontologies (in OWL or Turtle formats). The app loads your ontology file and presents it in two synchronized views: an interactive, full‑page graph (powered by pyvis) and an expandable/collapsible class hierarchy. The sidebar gives you control over the visualization, allowing you to filter nodes and edges, search for specific elements, and view detailed metadata—all without reloading the entire graph.

## Features

- Ontology Upload & Parsing:
  - Upload your ontology file via an auto‑submitting upload page.
  - The app automatically parses and loads the ontology for visualization.
- Interactive Graph View:
  - Explore the ontology with a dynamic, full‑page graph that supports smooth zooming and panning.
  - Click on any node to highlight all of its occurrences across the hierarchy and view its detailed information.
- Expandable Class Hierarchy:
  - Browse an intuitive tree view of the ontology’s classes.
  - If a node is a subclass of more than one class, all instances are highlighted when selected.
- Detailed Information Panel:
  - See complete details for any selected node—including its IRI, type, comments, and all metadata—in a panel that automatically wraps long text for readability.
- Node & Edge Filtering:
  - Use sidebar controls to toggle the visibility of different node types (classes, properties, individuals) and relationship types (subclass, instance, domain, range).
- Search Functionality:
  - Quickly locate nodes by typing into the search box, which dynamically filters the graph view.
- Adjustable & Collapsible Sidebar:
  - The sidebar is fully resizable and can be collapsed/reopened, giving you more screen space when needed while still providing quick access to all controls.
- Reset Functionality:
  - Easily undo all filtering, zooming, and layout changes with a reset button that restores the original graph view without the need to reload the entire graph.
- View New Graph:
  - Seamlessly return to the upload page to load a new ontology and start exploring a different graph.

## Prerequisites

- Python 3.7 or higher
- Git (optional)

## Quick Start

### For macOS/Linux:
```bash
curl -s https://raw.githubusercontent.com/fwromano/ontViz/main/setup.sh | bash
```
### For Windows(PowerShell):
```bash
iwr -useb https://raw.githubusercontent.com/fwromano/ontViz/main/setup.bat | iex
```
These one‑line commands will clone the repository (if needed), create a virtual environment, install dependencies, start the Flask server, and open your browser automatically.

If the project is already set up, you can simply launch the app:
### For macOS/Linux:
```bash
./launch.sh
```
### For Windows(PowerShell):
```bash
.\launch.bat
```

## Setup Instructions
If you prefer to set up and run the app manually, follow these steps:

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
ontViz/
├── app.py               # Main Flask application
├── templates/
│   └── index.html       # HTML template
│   └── uploads.html       # HTML template
├── static/              # Folder for generated files (e.g., graph.html)
├── uploads/             # Folder for uploaded ontology files
└── requirements.txt     # List of required packages
```