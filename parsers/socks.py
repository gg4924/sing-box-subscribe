import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    _netloc = (tool.b64Decode(server_info.netloc)).decode().split("@")
    netquery = dict(
        (k, v if len(v) > 1 else v[0])
        for k, v in parse_qs(server_info.query).items()
    )
    node = {
        'tag': tool.rename(netquery.get('remarks')),
        'type': 'socks',
        'server': re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0]),
        'server_port': int(_netloc[1].rsplit(":", 1)[1]),
        "version": "5",
        'username': _netloc[0].split(":")[0],
        'password': _netloc[0].split(":")[1],
        'udp_over_tcp': {}
    }
    return (node)