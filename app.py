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
    # Skip owl:Thing
    if cls == owlready2.Thing:
        return ""
    id_str = sanitize_id(str(cls.iri))
    name = cls.name if cls.name else str(cls)
    subs = [sub for sub in cls.subclasses() if sub != owlready2.Thing]
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
        if cls == owlready2.Thing:
            continue
        parents = [p for p in cls.is_a if isinstance(p, owlready2.entity.ThingClass)]
        if not parents or all(p == owlready2.Thing for p in parents):
            top.append(cls)
    return top

def readable_name(obj):
    """Convert an OWL entity or restriction into a readable string."""
    # Handle None values
    if obj is None:
        return "None"
    
    # Handle classes, properties, and individuals
    if isinstance(obj, (owlready2.ThingClass, owlready2.PropertyClass, owlready2.Thing)):
        # Use the IRI and take the part after the last '#' or '/' if available
        if hasattr(obj, 'iri') and obj.iri:
            iri = obj.iri
            return iri.split('#')[-1].split('/')[-1]
        # Fallback to name attribute or string representation
        return str(obj).split('.')[-1]
    
    # Handle restrictions (e.g., CanPerformAction some clear_rubble)
    elif isinstance(obj, owlready2.Restriction):
        prop = readable_name(obj.property)
        if obj.type == owlready2.SOME:
            value = readable_name(obj.value)
            return f"{prop} some {value}"
        elif obj.type == owlready2.ONLY:
            value = readable_name(obj.value)
            return f"{prop} only {value}"
        else:
            return str(obj)
    
    # Handle lists (e.g., is_a might be a list of classes and restrictions)
    elif isinstance(obj, list):
        return ", ".join(readable_name(item) for item in obj if item is not None)
    
    # Fallback for other types
    else:
        return str(obj)


def get_full_details(entity):
    """Retrieve all attributes and related properties of an entity."""
    details = {}

    for key in dir(entity):
        if key.startswith('_') or key in ('name', 'iri', 'comment'):
            continue
        try:
            value = getattr(entity, key)
            if not callable(value):
                details[key] = readable_name(value)
        except Exception:
            continue

    # If it's a class, add related properties
    if isinstance(entity, owlready2.ThingClass):
        related_out = []
        related_in = []

        for prop in ontology.object_properties():
            if entity in prop.domain:
                related_out.append(f"{prop.name} → {readable_name(prop.range)}")
            if entity in prop.range:
                related_in.append(f"{readable_name(prop.domain)} → {prop.name}")

        for prop in ontology.data_properties():
            if entity in prop.domain:
                related_out.append(f"{prop.name} → {readable_name(prop.range)}")
            if entity in prop.range:
                related_in.append(f"{readable_name(prop.domain)} → {prop.name}")

        if related_out:
            details["Outgoing Properties"] = "; ".join(related_out)
        if related_in:
            details["Incoming Properties"] = "; ".join(related_in)
    elif isinstance(entity, owlready2.Thing):
        prop_values = {}
        for prop in ontology.properties():
            if entity in prop.get_relations():
                values = prop[entity]
                if values:
                    prop_values[prop.name] = ", ".join(readable_name(v) for v in values)

        if prop_values:
            details["Property Values"] = "; ".join(f"{k}: {v}" for k, v in prop_values.items())

    return details


@app.route('/')
def index():
    if ontology is None:
        return redirect(url_for("upload"))
    
    group_colors = {
        'class': '#3498db',
        'property': '#e67e22',
        'individual': '#2ecc71'
    }
    
    net = Network(height="100%", width="100%", bgcolor="#222222", font_color="#eee")
    
    # Add nodes for classes, properties, and individuals, skipping owl:Thing.
    for cls in ontology.classes():
        if cls == owlready2.Thing:
            continue
        net.add_node(str(cls.iri), label=cls.name, title=str(cls.iri),
                     group="class", color=group_colors["class"])
    for prop in ontology.properties():
        net.add_node(str(prop.iri), label=prop.name, title=str(prop.iri),
                     group="property", color=group_colors["property"])
    for ind in ontology.individuals():
        net.add_node(str(ind.iri), label=ind.name, title=str(ind.iri),
                     group="individual", color=group_colors["individual"])
    
    # Add subclass edges (skip if superclass is owl:Thing).
    for cls in ontology.classes():
        if cls == owlready2.Thing:
            continue
        for sup in cls.is_a:
            if isinstance(sup, owlready2.entity.ThingClass) and sup != owlready2.Thing:
                net.add_edge(str(cls.iri), str(sup.iri), title="subClassOf")
    
    # Add individual type edges.
    for ind in ontology.individuals():
        for cls in ind.is_a:
            if isinstance(cls, owlready2.entity.ThingClass) and cls != owlready2.Thing:
                net.add_edge(str(ind.iri), str(cls.iri), title="instance_of")
    
    # Add property domain and range edges.
    for prop in ontology.properties():
        if hasattr(prop, "domain"):
            for d in prop.domain:
                if isinstance(d, owlready2.entity.ThingClass) and d != owlready2.Thing:
                    net.add_edge(str(prop.iri), str(d.iri), title="domain")
        if hasattr(prop, "range"):
            for r in prop.range:
                if isinstance(r, owlready2.entity.ThingClass) and r != owlready2.Thing:
                    net.add_edge(str(prop.iri), str(r.iri), title="range")
    
    graph_path = os.path.join("static", "graph.html")
    html_str = net.generate_html()
    
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
        tree_html = ""
    
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
    # Search in individuals if not found.
    if not entity:
        for ind in ontology.individuals():
            if str(ind.iri) == node_id:
                entity = ind
                entity_type = "Individual"
                break
    # Search in properties if still not found.
    if not entity:
        for prop in ontology.properties():
            if str(prop.iri) == node_id:
                entity = prop
                entity_type = "Property"
                break
    if not entity:
        return jsonify({'error': 'Entity not found'}), 404

    # Build a flat details dictionary.
    details = {}
    details['label'] = getattr(entity, "name", None) or str(entity)
    details['iri'] = str(entity.iri)
    details['type'] = entity_type

    if hasattr(entity, "comment"):
        if isinstance(entity.comment, list):
            details['comment'] = " ".join(entity.comment)
        else:
            details['comment'] = entity.comment

    # Add additional details.
    extra_details = get_full_details(entity)
    for key, value in extra_details.items():
        details[key] = value

    return jsonify(details)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
