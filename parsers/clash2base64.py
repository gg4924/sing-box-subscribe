import base64,json
from urllib.parse import quote, unquote

def clash2v2ray(share_link):
    link = ''
    if share_link['type'] == 'vmess':
        vmess_info = {
            "v": "2",
            "ps": share_link['name'].encode('utf-8', 'surrogatepass').decode('utf-8'),
            "add": share_link['server'],
            "port": share_link['port'],
            "id": share_link['uuid'],
            "aid": share_link['alterId'],
            "net": share_link['network'],
            "type": "none",
            "host": share_link.get('ws-opts', {}).get('headers', {}).get('Host') or share_link.get('ws-headers', {}).get('Host', ''),
            "path": share_link.get('ws-path', {}) or share_link.get('ws-opts', {}).get('path'),
            "tls": ""
        }
        vmess_json = json.dumps(vmess_info).encode('utf-8')
        vmess_base64 = base64.b64encode(vmess_json).decode('utf-8')
        link = f"vmess://{vmess_base64}"
        # TODO
    elif share_link['type'] == 'ss':
        ss_info = {
            "cipher": share_link['cipher'],
            "password": share_link['password'],
            "server": share_link['server'],
            "port": share_link['port'],
            "name": quote(share_link['name'], 'utf-8')
        }
        base_link = base64.b64encode("{cipher}:{password}".format(**ss_info).encode('utf-8')).decode('utf-8')
        if share_link.get('plugin'):
            ss_info["plugin"] = share_link['plugin']
            ss_info["mode"] = share_link['plugin-opts']['mode']
            ss_info["host"] = share_link['plugin-opts']['host']
            url_link = '/?plugin={plugin}%3Bobfs%3D{mode}%3Bobfs-host%3D{host}'.format(**ss_info)
            link = "ss://{base_link}@{server}:{port}{url_link}#{name}".format(base_link=base_link, url_link=url_link, **ss_info)
        else:
            link = "ss://{base_link}@{server}:{port}#{name}".format(base_link=base_link, **ss_info)
        # TODO
    elif share_link['type'] == 'ssr':
        ssr_info = {
            "server": share_link['server'],
            "port": share_link['port'],
            "protocol": share_link['protocol'],
            "cipher": share_link['cipher'],
            "obfs": share_link['obfs'],
            "password": base64.b64encode(share_link.get('password', '').encode('utf-8')).decode('utf-8'),
            "obfsparam": base64.b64encode(share_link.get('obfs-param', '').encode('utf-8')).decode('utf-8'),
            "protoparam": base64.b64encode(share_link.get('protocol-param', '').encode('utf-8')).decode('utf-8'),
            "remarks": base64.b64encode(share_link.get('name', '').encode('utf-8')).decode('utf-8'),
            "group": base64.b64encode(share_link.get('group', '').encode('utf-8')).decode('utf-8')
        }
        base_link = base64.b64encode("{server}:{port}:{protocol}:{cipher}:{obfs}:{password}/?obfsparam={obfsparam}&protoparam={protoparam}&remarks={remarks}&group={group}".format(**ssr_info).encode('utf-8')).decode('utf-8')
        link = f"ssr://{base_link}"
        # TODO
    elif share_link['type'] == 'trojan':
        link = "trojan://{password}@{server}:{port}?allowInsecure={allowInsecure}&peer={sni}sni={sni}{skip_cert_verify}#{name}".format(
        password = share_link['password'],
        server = share_link['server'],
        port = share_link['port'],
        allowInsecure = share_link['allowInsecure'] if share_link.get('allowInsecure') else "0",
        sni = share_link['sni'],
        skip_cert_verify = "&skip-cert-verify=1" if share_link.get('skip-cert-verify') else "",
        name = quote(share_link['name'], 'utf-8')
        )
    elif share_link['type'] == 'vless':
        vless_info = {
            "uuid": share_link['uuid'],
            "server": share_link['server'],
            "port": share_link['port'],
            "sni": share_link.get('servername', ''),
            "fp": share_link.get('client-fingerprint', ''),
            "type": share_link.get('network', 'tcp'),
            "flow": share_link.get('flow', ''),
            "name": quote(share_link['name'], 'utf-8')
        }   
        if vless_info['type'] == 'ws':
            vless_info["security"] = 'tls'
            vless_info["path"] = quote(share_link['ws-opts']['path'], 'utf-8')
            vless_info["host"] = share_link['ws-opts']['headers']['Host']
            link = "vless://{uuid}@{server}:{port}?encryption=none&security={security}&sni={sni}&fp={fp}&type={type}&host={host}&path={path}&flow={flow}#{name}".format(**vless_info)
        if vless_info['type'] == 'grpc':
            if share_link.get('grpc-opts').get('grpc-service-name') != '/' :
                vless_info["serviceName"] = unquote(share_link.get('grpc-opts').get('grpc-service-name'))
            else:
                vless_info["serviceName"] = ''
            if share_link.get('reality-opts'):
                vless_info["security"] = 'reality'
                vless_info["pbk"] = share_link['reality-opts']['public-key']
                vless_info["sid"] = share_link.get('reality-opts', {}).get('short-id', '')
                link = "vless://{uuid}@{server}:{port}?encryption=none&security={security}&sni={sni}&type={type}&serviceName={serviceName}&fp={fp}&flow={flow}&pbk={pbk}&sid={sid}#{name}".format(**vless_info)
            else:
                vless_info["security"] = 'tls'
                link = "vless://{uuid}@{server}:{port}?encryption=none&security={security}&sni={sni}&type={type}&serviceName={serviceName}&fp={fp}&flow={flow}#{name}".format(**vless_info)
        if vless_info['type'] == 'tcp':
            if share_link.get('reality-opts'):
                vless_info["security"] = 'reality'
                vless_info["pbk"] = share_link['reality-opts']['public-key']
                vless_info["sid"] = share_link.get('reality-opts', {}).get('short-id', '')
                link = "vless://{uuid}@{server}:{port}?encryption=none&security={security}&sni={sni}&serverName={sni}&type={type}&fp={fp}&flow={flow}&pbk={pbk}&sid={sid}#{name}".format(**vless_info)
            else:
                vless_info["security"] = 'tls'
                link = "vless://{uuid}@{server}:{port}?encryption=none&security={security}&sni={sni}&serverName={sni}&type={type}&fp={fp}&flow={flow}#{name}".format(**vless_info)
        # TODO
    return link
