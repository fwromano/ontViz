import os
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify
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
    Each <li> gets a data attribute based on the class IRI.
    """
    id_str = sanitize_id(str(cls.iri))
    name = cls.name if cls.name else str(cls)
    subs = list(cls.subclasses())
    if subs:
        html = f"<li data-node-iri='{id_str}'><span class='caret'>{name}</span>"
        html += "<ul class='nested'>"
        for sub in subs:
            html += generate_tree_html(sub)
        html += "</ul></li>"
    else:
        html = f"<li data-node-iri='{id_str}'>{name}</li>"
    return html

def get_top_level_classes():
    """Return classes with no parents (except owl:Thing)."""
    top = []
    for cls in ontology.classes():
        parents = [p for p in cls.is_a if isinstance(p, owlready2.entity.ThingClass)]
        if not parents or all(p == owlready2.Thing for p in parents):
            top.append(cls)
    return top

def get_full_details(entity):
    """Collect extra details by iterating over non-internal attributes."""
    details = {}
    for key in dir(entity):
        if key.startswith('_') or key in ('name', 'iri', 'comment'):
            continue
        try:
            value = getattr(entity, key)
            if not callable(value):
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value)
                details[key] = str(value)
        except Exception:
            continue
    return details

@app.route('/')
def index():
    if ontology is None:
        return redirect(url_for("upload"))
    
    # Define colors for node groups.
    group_colors = {
        'class': '#3498db',
        'property': '#e67e22',
        'individual': '#2ecc71'
    }
    
    net = Network(height="100%", width="100%", bgcolor="#222222", font_color="#eee")
    
    # Add nodes for classes, properties, and individuals.
    for cls in ontology.classes():
        net.add_node(str(cls.iri), label=cls.name, title=str(cls.iri),
                     group="class", color=group_colors["class"])
    for prop in ontology.properties():
        net.add_node(str(prop.iri), label=prop.name, title=str(prop.iri),
                     group="property", color=group_colors["property"])
    for ind in ontology.individuals():
        net.add_node(str(ind.iri), label=ind.name, title=str(ind.iri),
                     group="individual", color=group_colors["individual"])
    
    # Add subclass edges.
    for cls in ontology.classes():
        for sup in cls.is_a:
            if isinstance(sup, owlready2.entity.ThingClass):
                node_cls = str(cls.iri)
                node_sup = str(sup.iri)
                if node_cls not in net.get_nodes():
                    net.add_node(node_cls, color=group_colors["class"])
                if node_sup not in net.get_nodes():
                    net.add_node(node_sup, color=group_colors["class"])
                net.add_edge(node_cls, node_sup, title="subClassOf")
    
    # Add individual type edges.
    for ind in ontology.individuals():
        for cls in ind.is_a:
            if isinstance(cls, owlready2.entity.ThingClass):
                node_ind = str(ind.iri)
                node_cls = str(cls.iri)
                if node_cls not in net.get_nodes():
                    net.add_node(node_cls, label=cls.name or node_cls,
                                 title=node_cls, group="class", color=group_colors["class"])
                net.add_edge(node_ind, node_cls, title="instance_of")
    
    # Add property domain and range edges.
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
    
    # Inject custom CSS for a very dark gray full-viewport view.
    custom_css = """
    <style>
      html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        background: #111 !important;
        color: #eee !important;
      }
      #mynetwork {
        width: 100vw !important;
        height: 100vh !important;
      }
    </style>
    </head>
    """
    html_str = html_str.replace("</head>", custom_css)
    
    # Inject custom JS that listens for various postMessages.
    custom_js = """
    <script type="text/javascript">
      // When a node is clicked, notify the parent.
      network.on("click", function(params) {
        if (params.nodes.length > 0) {
          var nodeId = params.nodes[0];
          if (parent && typeof parent.highlightHierarchy === 'function') {
            parent.highlightHierarchy(nodeId);
          }
        }
      });
      
      // Listen for messages from the parent page.
      window.addEventListener("message", function(e) {
        var data = e.data;
        if (!data || !data.type) return;
        
        if (data.type === "updateNodeFilter") {
          var nodeTypes = data.nodeTypes;
          var search = data.search.toLowerCase();
          var nodes = network.body.data.nodes.get();
          nodes.forEach(function(node) {
            var typeVisible = (nodeTypes[node.group] === undefined ? true : nodeTypes[node.group]);
            var searchVisible = true;
            if (search && node.label) {
              searchVisible = node.label.toLowerCase().includes(search);
            }
            network.body.data.nodes.update({id: node.id, hidden: !(typeVisible && searchVisible)});
          });
        } else if (data.type === "toggleEdges") {
          var edgesFilter = data.edges;
          var edges = network.body.data.edges.get();
          edges.forEach(function(edge) {
            if (edge.title && edgesFilter.hasOwnProperty(edge.title)) {
              network.body.data.edges.update({id: edge.id, hidden: !edgesFilter[edge.title]});
            }
          });
        } else if (data.type === "resetView") {
          // Reset all nodes and edges to visible.
          var nodes = network.body.data.nodes.get();
          nodes.forEach(function(node) {
            network.body.data.nodes.update({ id: node.id, hidden: false });
          });
          var edges = network.body.data.edges.get();
          edges.forEach(function(edge) {
            network.body.data.edges.update({ id: edge.id, hidden: false });
          });
          network.fit();
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
          html, body {
            height: 100%;
            margin: 0;
            background-color: #111;
            color: #eee;
            font-family: Arial, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          form {
            display: flex;
            flex-direction: column;
            align-items: center;
          }
          input[type="file"] {
            padding: 8px;
          }
        </style>
      </head>
      <body>
        <form method="post" enctype="multipart/form-data">
          <h1>Upload Ontology File</h1>
          <input type="file" name="file" onchange="this.form.submit()">
        </form>
      </body>
    </html>
    '''

@app.route('/node_info')
def node_info():
    node_id = request.args.get('node_id')
    if not node_id:
        return jsonify({'error': 'No node id provided'}), 400
    entity = None
    entity_type = None
    # Search in classes.
    for cls in ontology.classes():
        if str(cls.iri) == node_id:
            entity = cls
            entity_type = "Class"
            break
    if not entity:
        for ind in ontology.individuals():
            if str(ind.iri) == node_id:
                entity = ind
                entity_type = "Individual"
                break
    if not entity:
        for prop in ontology.properties():
            if str(prop.iri) == node_id:
                entity = prop
                entity_type = "Property"
                break
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404

    label = getattr(entity, "name", None) or str(entity)
    comment = None
    if hasattr(entity, "comment"):
        if isinstance(entity.comment, list):
            comment = " ".join(entity.comment)
        else:
            comment = entity.comment

    basic_info = {
        'label': label,
        'iri': str(entity.iri),
        'type': entity_type,
        'comment': comment
    }
    full_details = get_full_details(entity)
    basic_info['all_details'] = full_details
    return jsonify(basic_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

