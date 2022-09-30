import requests
import urllib.parse


def get_res_uri(backend_server, res_type, res_name):
    """ Helper function to get a resource's uri
    :param backend_server: the backend server the request is going to be made to
    :param res_type: the resource's class
    :param res_name: the resource's name (i.e. rdfs:label or dc:title)
    :return: the uri of the resource
    """
    req_instance_url = urllib.parse.urljoin(
        backend_server,
        "resource?type={}&name={}".format(
            res_type, res_name))
    req_instance = requests.get(req_instance_url)
    if req_instance.status_code == 200:
        res = req_instance.json()
        res_uri = res.pop().get('resource') if res else ""
        return res_uri
