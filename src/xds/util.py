from uuid import uuid4
import time
import io
from xds.model import Document


__all__ = ['xdsuuid', 'to_mime']


def xdsuuid():
    xds_uuid = uuid4()
    i1 = int.from_bytes(xds_uuid.bytes[0:8], 'little')
    i2 = int.from_bytes(xds_uuid.bytes[8:16], 'little')
    i3 = int(round(time.time()*1000))

    return "{}.{}.{}".format(i1, i2, i3)


def to_mime(request, documents):

    domain = "xds.lakeside.dk"
    root = "root@{}".format(domain)
    boundary = "{}".format(str(uuid4()), domain)

    payload = io.StringIO()

    payload.write('--')
    payload.write(boundary)
    payload.write('\n')
    payload.write('Content-Type: text/xop+xml; charset="UTF-8"; type="text/xml"\n')
    payload.write('Content-Transfer-Encoding: binary\n')
    payload.write('Content-ID: <')
    payload.write(root)
    payload.write('>\n')
    payload.write('\n')
    payload.write(request)
    payload.write('\n')

    for d in documents:
        if isinstance(d, Document):
            payload.write('--')
            payload.write(boundary)
            payload.write('\n')
            payload.write('Content-Type: text/octet-stream\n')
            payload.write('Content-Transfer-Encoding: binary\n')
            payload.write('Content-ID: ')
            payload.write(d.mime_cid)
            payload.write('\n')
            payload.write('\n')
            print("Document data type:")
            print(type(d.data))
            payload.write(d.data)
            payload.write('\n')
        else:
            raise TypeError("Elements in documents are expected to be of type Document, got {}".format(type(d)))

    payload.write('--')
    payload.write(boundary)
    payload.write('--')
    payload.write('\n')

    return {"root": root,
            "boundary": boundary,
            "data": payload.getvalue()}
