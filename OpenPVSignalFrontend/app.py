import re
import requests
import urllib.parse

from itertools import chain
from functools import wraps

from itsdangerous import URLSafeSerializer
from flask import abort
from flask import flash
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import request
from flask import render_template
from flask import session
from flask import url_for

from flask_wtf.csrf import CSRFProtect

from helper_modules import get_res_uri
from view_subresources import resource_to_subresources


app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
csrf = CSRFProtect(app)
auth_token = URLSafeSerializer(app.secret_key)

backend_server = app.config['BACKEND_SERVER']


def auth_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        request_url = urllib.parse.urljoin(backend_server, 'auth')
        params = {"req": auth_token.dumps({"request": "permit_access"})}
        req = requests.get(request_url, params=params)
        ret_val = req.json()
        access = ret_val.get("access_flag")
        if not access:
            return abort(403)

        session["auth_id"] = ret_val.get("auth_id")

        # finally call f. f() now has access
        return f(*args, **kwargs)
    return wrap


@app.route('/', methods=['GET'])
@auth_required
def index():
    # Call rest api to get json object i.e. instances
    instances_url = urllib.parse.urljoin(backend_server, "reports")
    req = requests.get(instances_url)
    instances = []

    print(session["auth_id"])
    # instances variable refers to signal reports with all the appropriate info
    if req.status_code == 200:
        instances = req.json()
        session["res_view"] = {}

    return render_template('index.html', instances=instances)


@app.route('/edit', methods=['GET', 'POST'])
@auth_required
def edit():
    """ Post request to edit specific resource
    """
    if request.method == 'POST':
        instance_resource = request.form.get('resource')
        instance_name = request.form.get('name')
        graph_uri = request.form.get('graph_uri')

    else:
        rview = session["res_view"]
        instance_resource = rview.get('res_type')
        instance_name = rview.get('res_name')
        graph_uri = rview.get('res_graph_uri')

    session["res_view"] = {"res_type": instance_resource,
                           "res_name": instance_name,
                           "res_graph_uri": graph_uri
                           }

    # get_res_uri(backend_server, instance_resource, instance_name)
    graph_str = "&graph_uri={}".format(graph_uri) if graph_uri else ""
    title = instance_name.replace("_", " ")
    subresources_properties = resource_to_subresources[instance_resource]
    pending_resources = {}

    subresources = {}
    defaults = {}

    # parent_instance = instance_name
    for subresource in subresources_properties:
        if subresource in pending_resources.keys():
            # print(pending_resources[subresource])
            instance_name = pending_resources.pop(subresource)
        subres_props = subresources_properties[subresource]

        responses = {}

        # Make a request for a resource of specific name and type, add it to responses
        req_instance_url = urllib.parse.urljoin(
            backend_server,
            "resource?type={}&name={}{}&properties={}".format(
                subresource, instance_name, graph_str, list(subres_props.keys())))
        req_instance = requests.get(req_instance_url)

        if req_instance.status_code == 200:
            responses["resources_for_instance"] = req_instance.json()

        # Make a request for all resources of same type and add results to responses
        req_all_type_instances_url = urllib.parse.urljoin(
            backend_server,
            "resource?type={}{}&properties={}".format(
                subresource, graph_str, list(subres_props.keys())))
        req_all_type_instances = requests.get(req_all_type_instances_url)

        if req_all_type_instances.status_code == 200:
            responses["all_type_resources"] = req_all_type_instances.json()

        # In case of successful requests both for all type resources and specific instance
        if len(responses) == 2:

            subresources[subresource] = {}
            defaults[subresource] = {}

            # Initialize section keys to empty
            default_or_all = dict(zip(responses.keys(),
                                      [defaults, subresources]))

            for r in responses:
                for res in responses[r]:
                    for key in subres_props:
                        if subres_props[key].startswith("#"):
                            if key in res and r=="resources_for_instance":
                                pending_resources[subres_props[key].strip("#")] = res[key]
                        else:
                            label = subres_props[key]
                            if key.startswith("mp:"):
                                key = key.replace(":", "_")
                            default_or_all[r][subresource][label] = (default_or_all[r][subresource][label] if label in default_or_all[r][
                                subresource] else [instance_name] if label=="Label" else []) + ([res[key]] if key in res else [""])

    return render_template('edit_instance.html', subresources=subresources, defaults=defaults, title=title)


@app.route('/save', methods=['POST'])
@auth_required
def save():
    form_dict = request.form.to_dict(flat=False)

    http_referer = request.headers.get("Referer")
    resource_view = session.get("res_view")  # re.sub("&name=.*","", re.sub(".*\?resource=","", http_referer))
    resource_class = resource_view.get("res_type")

    resources = list(zip(form_dict["res_class"], form_dict["res_name"]))

    # indx shows depth level of subresources in form (relative to top level resource)
    for indx, res in enumerate(resources):
        # res_properties_values concerns each resource's properties
        res_properties_values = filter(lambda el: "{}_".format(indx) in el[0], form_dict.items())

        lbls_to_props = {v: k for k, v in resource_to_subresources[resource_class][res[0]].items()}

        # Find attached (sub)resources
        attached_resources = list(
            filter(lambda el: el.startswith("#"),
                   resource_to_subresources[resource_class][res[0]].values())
        )

        # Attached (sub)resource containing as value class and name of subresource
        att_prop_value = [(el, [get_res_uri(backend_server, el.replace("#", ""),
                                            dict(resources)[el.replace("#", "")])]) for el in attached_resources]

        res_properties_values = chain(res_properties_values, att_prop_value)

        # reverse to real property names instead of "human readable" labels
        res_properties_values = dict([(lbls_to_props[p.replace("{}_".format(indx),"")],
                                       pv.pop()) for p, pv in res_properties_values])

        update_params = {"type":res[0], "name": res[1],
                         "graph_uri": session["res_view"].get("res_graph_uri"),
                         "properties_values": res_properties_values}

        request_url = urllib.parse.urljoin(backend_server, 'update')
        req = requests.post(request_url, json = update_params)


    flash("Resources updated successfully!", "success")
    flash("Error! Resources could not be updated.", "error")
    return redirect(http_referer)


@app.route('/remove', methods=['GET', 'POST'])
@auth_required
def remove():
    return redirect(url_for('index'))

if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=3000)
