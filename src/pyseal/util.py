import io
from datetime import datetime

__all__ = ['timestamp', 'formatted_datetime', 'first', 'split_header',
           'MimeMultipart']


def timestamp():
    return datetime.utcnow()


def formatted_datetime(dt: datetime):
    assert dt is not None, "Datetime object is None."
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def first(item):
    if isinstance(item, list) and len(item) > 0:
        return item[0]
    else:
        return item


class MimeMultipart:

    def __init__(self):
        self.__part_header = []
        self.__part_content = []

    def count(self):
        return len(self.__part_header)

    def header(self, index):
        return self.__part_header[index]

    def content(self, index):
        if isinstance(index, int):
            return self.__part_content[index]
        else:
            content_id = str(index)
            part_idx = 0
            for ph in self.__part_header:
                for k, v in ph.items():
                    if k.lower() == 'content-id':
                        if v == content_id:
                            return self.__part_content[part_idx]
                part_idx += 1
            return None

    @staticmethod
    def parse(boundary, content):

        state = 0
        headers = {}
        part = ""

        mp = MimeMultipart()

        stream = io.StringIO(content)
        for line in stream:
            if state == 0: # Looking for boundary
                if line.rstrip() == "--" + boundary:
                    state = 1
                    headers = {}
                else:
                    print("'{}'".format(content))
                    raise ValueError("Expected boundary")
            elif state == 1: # Parsing headers
                if line.strip() == '':
                    state = 2
                    mp.__part_header.append(headers)
                    headers = {}
                else:
                    line = line.strip()
                    idx = line.find(":")
                    key = line[0:idx]
                    value = line[idx+1:].strip()
                    headers[key] = value
            elif state == 2: # Parse content
                if line.rstrip() == "--" + boundary:
                    mp.__part_content.append(part)
                    part = ""
                    state = 1
                elif line.rstrip() == "--" + boundary + "--":
                    print("Found part ...")
                    mp.__part_content.append(part)
                    part = ""
                    state = 3
                else:
                    part = part + line
            else:
                raise ValueError("Expected end of multipart content.")

        return mp


def split_header(header: str):
    result = {}
    parts = header.split(";")

    for part in parts:
        pair = part.split("=")
        if len(pair) == 1:
            value = pair[0].strip()
            result[None] = value
        elif len(pair) == 2:
            header = pair[0].strip()
            value = pair[1].strip()
            if (value.startswith('"') and value.endswith('"')) or \
                    (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            result[header] = value
        else:
            raise ValueError()

    return result