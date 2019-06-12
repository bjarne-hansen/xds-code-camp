from signxml import XMLSigner, XMLVerifier

__all__ = ['sign', 'verify']


def sign(element, reference_uri, certificate_data, key_data):

    signer = XMLSigner(signature_algorithm="rsa-sha1",
                       digest_algorithm="sha1",
                       c14n_algorithm="http://www.w3.org/2001/10/xml-exc-c14n#")

    # Sign XML.
    signed_element = signer.sign(element,
                                 key=key_data,
                                 cert=certificate_data,
                                 reference_uri=reference_uri)

    return signed_element


def verify(element, certificate_data):
    # Verify XML signature.
    verified_data = XMLVerifier().verify(element, x509_cert=certificate_data).signed_xml

    # Return verified data.
    return verified_data
