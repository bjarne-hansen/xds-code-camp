from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives import hashes
import base64

# Print certificate information.
cert_data = open("etc/FOCES_cert.pem", "rt").read().encode("ascii")
cert = x509.load_pem_x509_certificate(cert_data, default_backend())
print("Version: {}".format(cert.version))
print("Fingerprint: {}".format(cert.fingerprint(hashes.SHA256()).hex()))
print("Serial number: {}".format(cert.serial_number))
print("Public key: {}".format(cert.public_key()))
print("Not before: {}".format(cert.not_valid_before))
print("Not after: {}".format(cert.not_valid_after))
print("Issuer: {}".format(cert.issuer))
print("Subject: {}".format(cert.subject))
print("Hash: {}".format(cert.signature_hash_algorithm))
print("Signature OID: {}".format(cert.signature_algorithm_oid))

for e in cert.extensions:
    print("Extension: {}={}".format(e.oid, e.value))



# Generate base64 encoded SHA1 hash of a certificate
cert_data = open("etc/FOCES_cert.pem", "rt").read().encode("ascii")
cert = x509.load_pem_x509_certificate(cert_data, default_backend())
print(cert.serial_number)
print("'%s'" % base64.encodebytes(cert.fingerprint(hashes.SHA1())).decode().strip())
