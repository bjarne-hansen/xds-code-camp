from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import base64

__all__ = ["load_certificate_data", "certificate", "certificate_sha1_hash"]


def load_certificate_data(fname):
    cert_data = open(fname, "rt").read().encode("ascii")
    return cert_data


def certificate(data):
    cert = x509.load_pem_x509_certificate(data, default_backend())
    return cert


def certificate_sha1_hash(cert):
    return base64.encodebytes(cert.fingerprint(hashes.SHA1())).decode().strip()
