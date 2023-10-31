import tool,json,re,urllib,sys
from urllib.parse import urlparse, parse_qs, unquote
def parse(data):
    info = data[:]
    server_info = urlparse(info)
    node = {
        'tag': unquote(server_info.fragment)  or tool.genName()+'socks',
        'type': 'socks',
        "version": "5",
        'udp_over_tcp': {}
    }
    netloc = (tool.b64Decode(server_info.netloc)).decode()
    if '@' in netloc:
        _netloc = netloc.split("@")
        node['server'] = re.sub(r"\[|\]", "", _netloc[1].rsplit(":", 1)[0])
        node['server_port'] = int(_netloc[1].rsplit(":", 1)[1])
        node['username'] = _netloc[0].split(":")[0]
        node['password'] = _netloc[0].split(":")[1]
    else:
        node['server'] = re.sub(r"\[|\]", "", netloc.rsplit(":", 1)[0])
        node['server_port'] = int(netloc.rsplit(":", 1)[1])
    return (node)
