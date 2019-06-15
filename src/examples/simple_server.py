# Use Flask as REST API framework
# pip insatll flask
# See http://flask.pocoo.org/
from flask import Flask, request, Response

# Use lxml for etree compatible XML manipulation
# pip install lxml
# See https://lxml.de/
from lxml import etree as xml

# Use signxml for XML digital signature
# pip install signxml
# See https://github.com/XML-Security/signxml
from signxml import XMLVerifier

from XmlUtil import URI_SAML
from copy import deepcopy

import pyseal

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def root():
    print("Request URL: " + request.url)
    print("Query String: " + request.query_string.decode('utf-8') if request.query_string is not None else "")
    if request.args.get("message", None) is not None:
        return request.args.get("message")
    else:
        return "Hello world!"


__cert = pyseal.x509.load_certificate_data("etc/FOCES_cert.pem")
# __cert = open("etc/MOCES_cpr_gyldig.pem", "rt").read().encode("ascii")

@app.route("/multipart", methods=["POST"])
def multipart():

    for h, v in request.headers.items():
        print("{}: {}".format(h, v))

    print("Files: {}".format(len(request.files)))
    print("Data:\n{}".format(request.data.decode("utf-8")))

    return Response(status=200)


@app.route("/dgws", methods=["POST"])
def dgws():

    # Print request
    print("{} {}".format(request.method, request.url))

    # Deserialize XML content.
    text = request.get_data(as_text=True)
    document = xml.fromstring(text)

    # Extract assertion from XML document.
    assertion = pyseal.saml.get_assertion(document)
    if assertion is not None:
        verified_element = pyseal.dsig.verify(assertion, __cert)
        print("\n\nSigned Assertion:\n-----------------")
        print(xml.tostring(verified_element, pretty_print=True).decode("utf-8"))
        return Response("OK", status=200, content_type="text/plain")
    else:
        return Response("No assertion", status=400, content_type="text/plain")



    # Find assertion node and verify digital signature.
    # nodes = document.xpath("//saml:Assertion", namespaces={"saml": URI_SAML})
    # if len(nodes) > 0:
    #     # Copy assertion node to rip it out of the XML document tree as its own document.
    #     assertion = deepcopy(nodes[0])
    #
    #     # Verify XML signature.
    #     verified_data = XMLVerifier().verify(assertion, x509_cert=__cert).signed_xml
    #
    #     print(xml.tostring(verified_data, pretty_print=True).decode("utf-8"))
    #
    #     return Response("OK", status=200, content_type="text/plain")
    # else:
    #     return Response("Bad Request", status=400, content_type="text/plain")






