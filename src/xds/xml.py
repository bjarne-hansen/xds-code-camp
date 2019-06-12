import xds.model


def to_xml(obj):

    if isinstance(obj, xds.model.AdhocQueryRequest):
        pass

    elif isinstance(obj, xds.model.RetrieveDocumentSetRequest):
        pass

    else:
        raise TypeError("Invalid type in XML serialization {}".format(type(obj)))
