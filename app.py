import os
import re
from flask import Flask, render_template, request, redirect, url_for
import owlready2
from pyvis.network import Network

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Global ontology objects
ontology_world = None
ontology = None

# Ensure required folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("static", exist_ok=True)

def sanitize_id(s):
    """Replace one or more non-word characters with a single underscore."""
    return re.sub(r'\W+', '_', s)

def generate_tree_html(cls):
    """
    Recursively generate a collapsible tree HTML for a given class.
    Each <li> gets an id based on the class IRI.
    If the class has subclasses, a clickable <span class="caret"> is added.
    """
    id_str = sanitize_id(str(cls.iri))
    name = cls.name if cls.name else str(cls)
    subs = list(cls.subclasses())
    if subs:
        html = f"<li id='node_{id_str}'><span class='caret'>{name}</span>"
        html += "<ul class='nested'>"
        for sub in subs:
            html += generate_tree_html(sub)
        html += "</ul></li>"
    else:
        html = f"<li id='node_{id_str}'>{name}</li>"
    return html

def get_top_level_classes():
    """
    Return classes that do not have any parent other than owl:Thing.
    This yields a broader tree than just using owl:Thing.
    """
    top = []
    for cls in ontology.classes():
        parents = [p for p in cls.is_a if isinstance(p, owlready2.entity.ThingClass)]
        if not parents or all(p == owlready2.Thing for p in parents):
            top.append(cls)
    return top

@app.route('/')
def index():
    if ontology is None:
        return redirect(url_for("upload"))
    
    # Build the pyvis graph with 100% dimensions and dark styling.
    net = Network(height="100%", width="100%", bgcolor="#222222", font_color="white")
    
    # Add nodes for classes, properties, and individuals.
    for cls in ontology.classes():
        net.add_node(str(cls.iri), label=cls.name, title=str(cls.iri), group="class")
    for prop in ontology.properties():
        net.add_node(str(prop.iri), label=prop.name, title=str(prop.iri), group="property")
    for ind in ontology.individuals():
        net.add_node(str(ind.iri), label=ind.name, title=str(ind.iri), group="individual")
    
    # Add edges: subclass relationships.
    for cls in ontology.classes():
        for sup in cls.is_a:
            if isinstance(sup, owlready2.entity.ThingClass):
                node_cls = str(cls.iri)
                node_sup = str(sup.iri)
                if node_cls not in net.get_nodes():
                    net.add_node(node_cls)
                if node_sup not in net.get_nodes():
                    net.add_node(node_sup)
                net.add_edge(node_cls, node_sup, title="subClassOf")
    
    # Add edges: individual type assertions.
    for ind in ontology.individuals():
        for cls in ind.is_a:
            if isinstance(cls, owlready2.entity.ThingClass):
                net.add_edge(str(ind.iri), str(cls.iri), title="instance_of")
    
    # Add edges: property domain and range.
    for prop in ontology.properties():
        if hasattr(prop, "domain"):
            for d in prop.domain:
                if isinstance(d, owlready2.entity.ThingClass):
                    net.add_edge(str(prop.iri), str(d.iri), title="domain")
        if hasattr(prop, "range"):
            for r in prop.range:
                if isinstance(r, owlready2.entity.ThingClass):
                    net.add_edge(str(prop.iri), str(r.iri), title="range")
    
    # Generate the pyvis HTML.
    graph_path = os.path.join("static", "graph.html")
    html_str = net.generate_html()
    
    # Inject CSS to remove any white space and force a dark full-viewport view.
    custom_css = """
    <style>
      html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background: #222 !important;
      }
      #mynetwork {
        width: 100vw !important;
        height: 100vh !important;
      }
    </style>
    </head>
    """
    html_str = html_str.replace("</head>", custom_css)
    
    # Inject JS so that a node click notifies the parent page.
    custom_js = """
    <script type="text/javascript">
      network.on("click", function(params) {
        if (params.nodes.length > 0) {
          var nodeId = params.nodes[0];
          if (parent && typeof parent.highlightHierarchy === 'function') {
            parent.highlightHierarchy(nodeId);
          }
        }
      });
    </script>
    </body>"""
    html_str = html_str.replace("</body>", custom_js)
    
    with open(graph_path, "w") as f:
        f.write(html_str)
    
    # Build the hierarchy tree.
    top_classes = get_top_level_classes()
    if top_classes:
        tree_html = "<ul>"
        for cls in top_classes:
            tree_html += generate_tree_html(cls)
        tree_html += "</ul>"
    else:
        root_class = getattr(ontology, "Thing", None) or owlready2.Thing
        tree_html = "<ul>" + generate_tree_html(root_class) + "</ul>"
    
    return render_template("index.html", tree_html=tree_html)

@app.route('/upload', methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)
            global ontology_world, ontology
            ontology_world = owlready2.World()
            ontology = ontology_world.get_ontology("file://"+os.path.abspath(file_path)).load()
            return redirect(url_for("index"))
        return "No file uploaded", 400
    return '''
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Upload Ontology</title>
        <style>
          body { background-color: #222; color: white; font-family: Arial, sans-serif; padding: 20px; }
          input { padding: 8px; }
        </style>
      </head>
      <body>
        <h1>Upload Ontology File</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file"><br><br>
          <input type="submit" value="Upload">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True)
