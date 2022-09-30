from datetime import datetime

import ast
import rdflib
import uuid

from itsdangerous import URLSafeSerializer
from flask import Flask
from flask import request
from flask import jsonify

from helper_modules import OpenPVSignalWrapper


app = Flask(__name__)
app.config.from_object('config.Config')
# sel_graph = None
opvsw = OpenPVSignalWrapper()
auth_token = URLSafeSerializer(app.secret_key)


@app.route('/auth', methods=['GET'])
def user_allowed():
    token_dic = auth_token.loads(request.args.get('req'))
    auth_ret = {"access_flag": (token_dic.get("request") == "permit_access"),
                "auth_id": uuid.uuid4()}

    # if auth_ret.get("access_flag"):
    #     session[auth_ret.get("auth_id")] = []

    return jsonify(auth_ret)


@app.route('/reports', methods=['GET'])
def get_reports():
    """ Get all instances/entities concerning Pharmacovigilance Signal Reports
    """

    reports = opvsw.get_reports()

    instances = []

    if (len(reports) == 0):
        print("No reports found.")
    else:
        for report in reports:
            instance = {}
            edited_by = "bdimitriadis"

            # Get list with contained properties in report, concerning report title or label
            instance['graph_uri'] = report['graph_uri'].value if 'graph_uri' in report else ""
            title_properties_contained =[report[p].value for p in report if p in ['title', 'label']] + [""]
            instance['signal_report'] = title_properties_contained[0]
            instance['signal_report_url'] = report['report'].value if 'report' in report else ""
            instance['author'] = report['author_name'].value if 'author_name' in report else ""
            instance['edited_by'] = edited_by
            instance['last_edit'] = datetime.today().strftime("%d/%m/%Y")
            _, instance['name'] = instance['signal_report_url'].split('#')
            instance['resource'] = 'Pharmacovigilance_Signal_Report'
            instances.append(instance)

    return jsonify(instances)


@app.route('/drugs', methods=['GET'])
def get_drugs():
    sel_graph = request.args.get('graph')

    store = surf.Store(reader="sparql_protocol",
                       writer="sparql_protocol",
                       endpoint=sparql_endpoint,
                       default_graph=sel_graph)
    # "http://purl.org/OpenPVSignal/lareb_2013_3_esomeprazole_tinnitus"

    # store.load_triples(source = "http://purl.org/OpenPVSignal/lareb_2013_3_esomeprazole_tinnitus")
    session = surf.Session(store)

    # store.load_triples(source = "http://purl.org/OpenPVSignal/lareb_2013_3_esomeprazole_tinnitus")

    Drug = session.get_class(surf.ns.OPVS['Drug'])
    all_drugs = Drug.all()

    drugs = [(d.rdfs_label.first.toPython() if d.rdfs_label
              else surf.util.uri_split(d.subject)[1]).capitalize() for d in
             all_drugs]

    session.close()
    return jsonify(list(drugs))


@app.route('/resource', methods=['GET', 'POST'])
def get_resources():
    """ Get specific resource or all resources of specific type
    if name parameter is not send with the request
    """
    instance_class = request.args.get('type')
    instance_name = request.args.get('name', default="")
    graph_uri = request.args.get('graph_uri', default="")

    # Properties belonging to opvs should have ns for namespace
    properties = request.args.get('properties')

    instance_properties = ast.literal_eval(properties) if properties else []

    # Get resources for specific name instance (default values of fields)
    results = opvsw.get_resources(instance_class, name=instance_name,
                                  graph_uri=graph_uri, properties=instance_properties)

    resources = []
    for result in results:
        resource = ((r.replace("ns_", "").replace("_value", ""), result[r]) for r in result)
        resources.append(dict(resource))

    return jsonify(resources)


@app.route('/update', methods=['GET', 'POST'])
def update_resource():
    """ Update old property values for a subresource of specific name and class
    with the new property values or just insert new subresource.
    Then update parent resource
    :return: update_status
    """

    req_json = request.get_json()

    # Properties belonging to opvs should have ns for namespace
    properties_values = req_json.get('properties_values')
    instance_class = req_json.get('type')
    instance_name = req_json.get('name') or ""
    graph_uri = req_json.get('graph_uri') or ""

    # Get properties to be changed, to retrieve their initial values
    properties, _ = zip(*properties_values.items())

    results = opvsw.get_resources(instance_class, name=instance_name,
                                  graph_uri=graph_uri, properties=properties) if instance_name else []

    if results:
        # The initial values of the specific properties
        init_prop_vals = dict([(item[0].replace("_value", "").replace("_", ":", 1).replace(
            "ns:", ""), item[1]) for item in results.pop().items() if item[0]!='resource'])

        ret_val = opvsw.update_resource(instance_class, name=instance_name,
                                        graph_uri=graph_uri,
                                        init_properties_values=init_prop_vals,
                                        properties_values=properties_values)

    else:
        ret_val = "must_insert"
    
    return jsonify(ret_val)


if __name__ == '__main__':
    app.run()
