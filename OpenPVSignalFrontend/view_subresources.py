# The subresources each resource consists of
# and the properties of each subresource we are
# going to need (as far as view is concerned)

resource_to_subresources = {
    "Pharmacovigilance_Signal_Report": {
        "Pharmacovigilance_Signal_Report": {
            # "rdfs:isDefinedBy": "Is defined by",
            "mp:publishedBy": "Published by",
            "refers_to_author": "Refers to author",
            "refers_to_signal": "#Signal",
        },
        "Signal": {
                "rdfs:label": "Label",
                "refers_to_drug": "#Drug",
        },
        "Drug": {"rdfs:label": "Label", "has_ATC_code": "ATC", "refers_to_adverse_effect": "#Adverse_Effect"},
        "Adverse_Effect": {"rdfs:label": "Label", "has_ICD_code": "ICD"},
    }
}