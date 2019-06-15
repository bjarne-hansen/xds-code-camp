from uuid import uuid4
import time

# private String generateUUID()
# {
#   java.util.UUID uuid = java.util.UUID.randomUUID();
#   return Math.abs(uuid.getLeastSignificantBits()) + "." + Math.abs(uuid.getMostSignificantBits())+"."+Calendar.getInstance().getTimeInMillis();
# }


def xdsuuid():
    id = uuid4()
    i1 = int.from_bytes(id.bytes[0:8], 'little')
    i2 = int.from_bytes(id.bytes[8:16], 'little')
    i3 = int(round(time.time()*1000))

    return "{}.{}.{}".format(i1, i2, i3)

