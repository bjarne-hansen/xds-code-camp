import requests
from uuid import uuid4
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


if __name__ == "__main__":

    # files = {'file': ('file1.txt', 'Dette er en test')}
    #
    # headers = {
    #     "Content-Type":
    #         'multipart/related; type="application/xop+xml"; boundary="uuid:52a6c54a-20db-4aba-bf36-2ac132997b00"; '
    #         'start="<root.message@cxf.apache.org>"; start-info="text/xml"'
    # }
    #
    # requests.post("http://localhost:5000/multipart", headers=headers, files=files)
    # related = MIMEMultipart('related; type="application/xop+xml"; start="<root.message@cxf.apache.org>"; '
    #                        'start-info="text/xml"', boundary="DEADBEEF")
    related = MIMEMultipart('related', "DEADBEEF",
                            **{"type": "application/xop+xml",
                                     "start": "<root.message@cxf.apache.org>",
                                     "start-info": "text/xml"})
    del related["MIME-Version"]

    part = MIMEText("application", "xop+xml", "utf-8")
    del part["Content-Transfer-Encoding"]
    del part["MIME-Version"]
    part["Content-Transfer-Encoding"] = "binary"
    part["Content-ID"] = "<root@pyxds.lakeside.dk"
    part.set_payload("Part1")
    related.attach(part)

    part = MIMEText("application", "octet-stream", "utf-8")
    del part["Content-Transfer-Encoding"]
    del part["MIME-Version"]
    part["Content-Transfer-Encoding"] = "binary"
    part["Content-ID"] = "<{}>".format(str(uuid4()) + "@pyxds.lakeside.dk")

    part.set_payload("Part2")
    related.attach(part)

    body = related.as_string().split('\n\n', 1)[1]
    headers = dict(related.items())



    print(related)
    # for k, v in headers.items():
    #     print("{}: {}".format(k, v))
    # print(body)
