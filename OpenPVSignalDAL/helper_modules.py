from SPARQLWrapper import SPARQLWrapper2
from SPARQLWrapper import JSON

from config import SparqlConfig


class OpenPVSignalWrapper:
    def __init__(self):
        self.sparql = SPARQLWrapper2(SparqlConfig.sparql_endpoint)
        self.sparql.setCredentials(user=SparqlConfig.username,
                                   passwd=SparqlConfig.password,
                                   realm=SparqlConfig.realm)
        self.sparql.setHTTPAuth(SparqlConfig.auth)
        self.sparql.setReturnFormat(JSON)

    def get_resources(self, class_name, name="", graph_uri=None, properties=[], sparql_prefixes=SparqlConfig.sparql_prefixes):
        """Get resource (and their properties if properties parameter is not []) of specific class,
        name and namespace. If name is None, get all resources of the specific type/class
        :param class_name: the name of the resource's class
        :param name: the name of the resource or None
        :param graph_uri: the specific graph where someone should look for the resource
        :param properties: properties of resource to get
        :param sparql_prefixes: defaults to SparqlConfig.sparql_prefixes
        :return: one or more resources fulfilling the parameters' criteria
        """

        # If : not in property, add ns prefix for namespace
        properties = list(map(lambda el: el if ":" in el else "ns:{}".format(el), properties))

        # String with properties' names joined for the whole query to retrieve properties' values
        properties_values = ["?{}_value".format(p).replace(":", "_") for p in properties]
        properties_uris = ["?{}_value_uri".format(p).replace(":", "_") for p in properties]

        pvalues_queries = ",".join(["?resource"]+properties_values+properties_uris)

        # String with properties' queries joined in order to build up the whole query
        properties_queries = "\n".join(["optional{{?resource {0} {1}_uri.\n"
                                        "{1}_uri rdfs:label {1}}}."
                                        "optional{{?resource {0} {1}}}.\n".format(p,v)
                                        for p, v in zip(properties,properties_values)])

        name_query = """{{?resource dc:title \"{0}\"}}
                        UNION {{?resource rdfs:label \"{0}\"}}.
                    """.format(name) if name else ""
        use_graph = "GRAPH <{}>".format(graph_uri) if graph_uri else ""

        prefixes_str = "\n".join(["PREFIX {}: <{}>".format(k,v) for k, v in sparql_prefixes.items()])

        whole_query = """
                {}
                select {}
                where {{
                {}
                {{?resource a ns:{}.
                    {}
                    {}}}
                }}
            """.format(prefixes_str, pvalues_queries, use_graph,
                       class_name, name_query, properties_queries)

        self.sparql.setQuery(whole_query)
        results = self.sparql.query().bindings

        pvalues_stripped = list(map(lambda el: el.strip("?"), properties_values))

        # Fill empty attributes/properties with "" and turn SPARQLWrapper Value type to value in results
        results = [dict(
            dict(map(lambda el: (el[0], el[1].value), result.items())),
            **dict([(k, "") for k in filter(lambda pv: pv not in result, pvalues_stripped)])
        ) for result in results]

        return results

    def update_resource(self, class_name, name="", graph_uri=None, properties_values={},
                        init_properties_values={}, sparql_prefixes=SparqlConfig.sparql_prefixes):
        """
        :param class_name: the name of the resource's class
        :param name: the name of the resource or None
        :param graph_uri: the specific graph where someone should look for the resource
        :param init_properties_values: properties of the resource to update and the old values
        :param properties_values: properties of the resource to update and the updated/new values
        :param sparql_prefixes: defaults to SparqlConfig.sparql_prefixes
        :return: update status
        """

        properties, pvalues = zip(*properties_values.items())

        # Resource property value needs to be a uri not a label when uri available e.g. refers_to_drug
        init_pvalues = [init_properties_values[p] if "{}_uri".format(p)\
                        not in init_properties_values.keys() else \
                init_properties_values["{}_uri".format(p)] for p in properties]


        # If : not in property, add ns prefix for namespace
        properties = list(map(lambda el: el if ":" in el else "ns:{}".format(el), properties))

        # String with properties' delete queries joined in order to build up the whole query
        delete_queries = ";\n".join([" {} \"{}\"".format(p,v)
                                        for p, v in zip(properties, init_pvalues)])

        delete_queries = "?resource{}".format(delete_queries)

        # String with properties' insert queries joined in order to build up the whole query
        insert_queries = ";\n".join([" {} \"{}\"".format(p,v)
                                        for p, v in zip(properties, pvalues)])
        insert_queries = "?resource{}".format(insert_queries)

        # In case name is not given for the query, find resource by its properties' values
        by_attrs_part = "\n".join(["{{?resource {0} ?p_{1}_uri.\n"
                                   "?p_{1}_uri rdfs:label \"{2}\"}}UNION"
                                   "{{?resource {0} \"{2}\"}}.\n".format(
            p if ":" in p else "ns:{}".format(p), p.replace(":", "_"), v
        ) for p, v in init_properties_values.items()])

        where_part = """{{?resource a \"ns:{1}\".
                ?resource dc:title {0}}} UNION {{?resource rdfs:label \"{0}\"}}.""".format(
            name, class_name) if not name and class_name else "{{?resource a ns:{0}.\n {1} }}.".format(
            class_name, by_attrs_part)


        use_graph = "WITH <{}>".format(graph_uri) if graph_uri else ""

        prefixes_str = "\n".join(["PREFIX {}: <{}>".format(k, v) for k, v in sparql_prefixes.items()])

        whole_query = """
                        {}
                        {}
                        delete {{ {} }}
                        insert {{ {} }}
                        where {{
                        {}

                        }}
                    """.format(prefixes_str, use_graph, delete_queries,
                               insert_queries, where_part)
        return whole_query



    def insert_resource(self, class_name, name="", graph_uri=None, properties_values=[],
                        sparql_prefixes=SparqlConfig.sparql_prefixes):
        """
        :param class_name: the name of the resource's class
        :param name: the name of the resource or None
        :param graph_uri: the specific graph where someone should look for the resource
        :param properties_values: properties of the resource to insert and their values
        :param sparql_prefixes: defaults to SparqlConfig.sparql_prefixes
        :return: insert status
        """
        pass


    def get_reports(self, sparql_prefixes=SparqlConfig.sparql_prefixes):
        """Get instances of specific class and namespace

        :param name_space: defaults to opvs namespace:
        :return: reports query results
        """

        prefixes_str = "\n".join(["PREFIX {}: <{}>".format(k, v) for k, v in sparql_prefixes.items()])
        whole_query = """
                {}
                select ?graph_uri, ?report, ?title, ?label, ?author_name
                where {{
                GRAPH ?graph_uri
                    {{
                        ?report a ns:Pharmacovigilance_Signal_Report.
                        optional {{?report dc:title ?title}}.
                        optional {{?report rdfs:label ?label}}.
                        ?report ns:refers_to_author ?author.
                        ?author rdfs:label ?author_name
                    }}
                }}
            """.format(prefixes_str)
        
        self.sparql.setQuery(whole_query)
        results = self.sparql.query().bindings
        return results
