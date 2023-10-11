import base64,json,re
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
            "net": share_link.get('network', 'tcp'),
            "scy": share_link.get('cipher', 'auto'),
            "type": "none",
            "host": share_link.get('ws-opts', {}).get('headers', {}).get('Host', '') or share_link.get('ws-headers', {}).get('Host', ''),
            "path": share_link.get('ws-path', '') or share_link.get('ws-opts', {}).get('path', ''),
            "tls": ''
        }
        if share_link.get('skip-cert-verify') == True:
            vmess_info['verify_cert'] = True
        if share_link.get('tls') and share_link['tls'] != False:
            vmess_info['tls'] = 'tls'
        if vmess_info['net'] == 'grpc':
            vmess_info["type"] = share_link.get('grpc-opts', {}).get('grpc-mode')
            vmess_info["sni"] = share_link.get('servername', '')
            if share_link.get('grpc-opts', {}).get('grpc-service-name') != '/':
                vmess_info["path"] = share_link.get('grpc-opts', {}).get('grpc-service-name')
            else:
                vmess_info["path"] = ''
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
            if share_link.get('plugin') == 'shadow-tls':
                ss_info["shadowtls_password"] = share_link['plugin-opts']['password']
                ss_info["version"] = share_link['plugin-opts']['version']
                ss_info["host"] = share_link['plugin-opts']['host']
                shadowtls = f'{{"version": "{ss_info["version"]}", "host": "{ss_info["host"]}","password": "{ss_info["shadowtls_password"]}"}}'
                url_link = f'?shadow-tls={base64.b64encode(shadowtls.encode()).decode()}'
            if share_link.get('plugin') == 'obfs':
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
        trojan_info = {
            "password": share_link['password'],
            "server": share_link['server'],
            "port": share_link['port'],
            "allowInsecure": share_link.get('allowInsecure', '1'),
            "sni": share_link.get('sni', ''),
            "skip_cert_verify": '1' if share_link.get('skip-cert-verify') else "",
            "type": share_link.get('network', 'tcp'),
            "fp": share_link.get('client-fingerprint', ''),
            "alpn": quote(','.join(share_link.get('alpn', '')), 'utf-8'),
            "name": quote(share_link['name'], 'utf-8')
        }
        if trojan_info['type'] == 'grpc':
            if share_link.get('grpc-opts').get('grpc-service-name') != '/' :
                trojan_info["serviceName"] = unquote(share_link.get('grpc-opts').get('grpc-service-name'))
            else:
                trojan_info["serviceName"] = ''
            link = "trojan://{password}@{server}:{port}?allowInsecure={allowInsecure}&sni={sni}&skip_cert_verify={skip_cert_verify}&type={type}&serviceName={serviceName}&fp={fp}&alpn={alpn}#{name}".format(**trojan_info)
        if trojan_info['type'] == 'ws':
            if share_link.get('ws-opts'):
                trojan_info["path"] = quote(share_link['ws-opts'].get('path', ''), 'utf-8')
                trojan_info["host"] = share_link.get('ws-opts', {}).get('headers', {}).get('Host', '')
            else:
                trojan_info["path"] = ''
                trojan_info["host"] = trojan_info["sni"]
            link = "trojan://{password}@{server}:{port}?allowInsecure={allowInsecure}&sni={sni}&skip_cert_verify={skip_cert_verify}&type={type}&host={host}&path={path}&fp={fp}&alpn={alpn}#{name}".format(**trojan_info)
        if trojan_info['type'] == 'tcp':
            link = "trojan://{password}@{server}:{port}?allowInsecure={allowInsecure}&sni={sni}&skip_cert_verify={skip_cert_verify}&type={type}&fp={fp}&alpn={alpn}#{name}".format(**trojan_info)
        # TODO
    elif share_link['type'] == 'vless':
        vless_info = {
            "uuid": share_link['uuid'],
            "server": share_link['server'],
            "port": share_link['port'],
            "sni": share_link.get('servername', share_link.get('sni')),
            "fp": share_link.get('client-fingerprint', ''),
            "type": share_link.get('network', 'tcp'),
            "flow": share_link.get('flow', ''),
            "name": quote(share_link['name'], 'utf-8')
        }
        if vless_info['type'] == 'ws':
            vless_info["security"] = 'tls'
            vless_info["path"] = quote(share_link['ws-opts'].get('path', ''), 'utf-8')
            vless_info["host"] = share_link['ws-opts']['headers'].get('Host', '')
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
    elif share_link['type'] == 'tuic':
        link = "tuic://{uuid}:{password}@{server}:{port}?alpn={alpn}&allow_insecure={allowInsecure}&disable_sni={disable_sni}&sni={sni}&udp_relay_mode={udp_relay_mode}&congestion_control={control}#{name}".format(
        uuid = share_link['uuid'],
        password = share_link['password'],
        server = share_link['server'],
        port = share_link['port'],
        alpn = quote(','.join(share_link.get('alpn', '')), 'utf-8'),
        allowInsecure = share_link.get('allowInsecure', '1'),
        disable_sni = '0' if share_link.get('disable-sni', '') == False else '1',
        sni = share_link.get('sni', ''),
        udp_relay_mode = share_link.get('udp-relay-mode', 'native'),
        control = share_link.get('congestion-controller', 'bbr'),
        name = share_link['name'].encode('utf-8', 'surrogatepass').decode('utf-8')
        )
        # TODO
    elif share_link['type'] == 'hysteria':
        link = "hysteria://{server}:{port}?protocol={protocol}&auth={auth}&alpn={alpn}&insecure={allowInsecure}&peer={sni}&upmbps={upmbps}&downmbps={downmbps}&obfs={obfs}#{name}".format(
        server = share_link['server'],
        port = share_link['port'],
        protocol = share_link.get('port', 'udp'),
        auth = share_link.get('auth_str', share_link.get('auth-str')),
        alpn = quote(','.join(share_link.get('alpn', '')), 'utf-8'),
        allowInsecure = '0' if share_link.get('skip-cert-verify', '') == False else '1',
        sni = share_link.get('sni', ''),
        upmbps = int(re.search(r'\d+', str(share_link.get('up', '')))[0]),
        downmbps = int(re.search(r'\d+', str(share_link.get('down', '')))[0]),
        obfs = share_link.get('obfs', ''),
        name = share_link['name'].encode('utf-8', 'surrogatepass').decode('utf-8')
        )
        # TODO
    elif share_link['type'] == 'hysteria2':
        link = "hysteria2://{auth}@{server}:{port}?insecure={allowInsecure}&obfs={obfs}&obfs-password={obfspassword}&pinSHA256={fingerprint}&sni={sni}&alpn={alpn}&upmbps={upmbps}&downmbps={downmbps}#{name}".format(
        auth = share_link['password'],
        server = share_link['server'],
        port = share_link['port'],
        allowInsecure = '0' if share_link.get('skip-cert-verify', '') == False else '1',
        obfs = share_link.get('obfs', ''),
        obfspassword = share_link.get('obfs-password', ''),
        fingerprint = share_link.get('fingerprint', ''),
        sni = share_link.get('sni', ''),
        alpn = quote(','.join(share_link.get('alpn', '')), 'utf-8'),
        upmbps = share_link.get('up', ''),
        downmbps = share_link.get('down', ''),
        name = share_link['name'].encode('utf-8', 'surrogatepass').decode('utf-8')
        )
        # TODO
    elif share_link['type'] == 'wireguard':
        link = "wg://{server}:{port}?publicKey={publicKey}&privateKey={privateKey}&presharedKey={presharedKey}&ip={ip},{ipv6}&udp=1&reserved={reserved}#{name}".format(
        server = share_link['server'],
        port = share_link['port'],
        publicKey = share_link['public-key'],
        privateKey = share_link['private-key'],
        presharedKey = share_link.get('pre-shared-key', ''),
        ip = share_link['ip'],
        ipv6 = share_link.get('ipv6', ''),
        reserved = ','.join(str(item) for item in share_link['reserved']),
        name = quote(share_link['name'], 'utf-8')
        )
        # TODO
    elif share_link['type'] == 'http':
        http_info = {
            "user": share_link['username'],
            "password": share_link['password'],
            "server": share_link['server'],
            "port": share_link['port'],
        }
        name = quote(share_link.get('name', ''), 'utf-8')
        base_link = base64.b64encode("{user}:{password}@{server}:{port}".format(**http_info).encode('utf-8')).decode('utf-8')
        link = f"http://{base_link}#{name}"
        if share_link.get('tls') == True:
            link = f"http://{base_link}?tls=1#{name}"
        # TODO
    elif share_link['type'] == 'socks5':
        socks5_info = {
            "user": share_link['username'],
            "password": share_link['password'],
            "server": share_link['server'],
            "port": share_link['port'],
        }
        base_link = base64.b64encode("{user}:{password}@{server}:{port}".format(**socks5_info).encode('utf-8')).decode('utf-8')
        link = f"socks5://{base_link}"
        # TODO
    return link
