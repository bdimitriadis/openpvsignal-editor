class Config(object):
    """ App config
    """
    SECRET_KEY = <BYTES_LITERAL_SECRET_KEY>

class SparqlConfig(object):
    """ SPARQL config
    """
    # e.g. sparql_endpoint = "http://<someip>:8890/sparql"  #
    sparql_endpoint = <SPARQL_URI>
    sparql_prefixes = {
        "ns": "http://purl.org/OpenPVSignal/OpenPVSignal.owl#",
        "mp": "http://purl.org/mp/",
        # "dc": "http://purl.org/dc/elements/1.1/"

    }
    username = <SPARQL_USERNAME>
    password = <SPARQL_USERPASSWORD>

    realm = "SPARQL Endpoint"  # Default value is SPARQL

    auth = "DIGEST"  # Default value is BASIC
