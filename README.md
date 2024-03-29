# sing-box-subscribe
对不起，可能不会更新了，最近也没有关注sing-box的更新，在使用别的工具。sing-box是很好的工具，没有继续使用sing-box的原因是它不能像clash一样热更新配置（不重启工具以及不断开活动连接的情况下更新规则以及节点等配置信息），不知道是我没找到方法还是什么，也不知道现在更新了没有。另sing-box也和我现在使用的某些工具有冲突。

有想继续使用脚本的小伙伴可以移步到[https://github.com/Toperlock/sing-box-subscribe](https://github.com/Toperlock/sing-box-subscribe)，这个项目完善了很多功能，也在跟进更新。

根据配置模板生成 sing-box 使用的 config.json，主要用于将机场订阅节点添加到 config，对使用 clash_mode 的配置才有意义。
不适合完全不了解 sing-box 配置文件的人使用，最少要知道什么是出站、dns server、dns规则、路由规则。最好了解 clash 的分组方式。

请查看：[https://sing-box.sagernet.org/zh/configuration](https://sing-box.sagernet.org/zh/configuration)。

不支持转换 clash 配置订阅，暂时只写了 vmess、trojan、ss、ssr 协议的分享链接的解析，因为自己用的机场只有这几个协议，vless等其他没有。添加新的协议解析有能力可以自己写，比如 vless.py（文件名称必须为协议名称），写好后将其放入到 parsers 目录即可，vless.py 中必须包含 parse 函数。

**脚本为自用，本人使用 [yacd](https://github.com/haishanh/yacd) 进行节点切换管理（类型为urltest、selector的出站），配合规则像clash一样分流，非常方便。需求跟我一样的可以尝试，但使用脚本过程中有新的功能需求或者出现任何错误请自行解决**。
# 环境
需要安装最新版本 python，并安装下面的依赖：
```
pip install requests paramiko scp
```
使用下面的命令运行脚本：
```
python main.py
```
windows系统建议将命令添加到批处理程序运行。

使用前先编辑 providers.json 文件以及 config_template 目录下的 json 模板文件。
# providers.json文件
在这个文件中添加订阅链接，以及基础设置。
```json
{
    "subscribes":[
        {
            "url": "订阅地址1",
            "tag": "机场1",
            "enabled": true
        },
        {
            "url": "订阅地址2",
            "tag": "机场2",
            "enabled": false,
            "prefix": "❤️机场前缀 - "
        }
    ],
    "auto_set_outbounds_dns":{
        "proxy": "remote_cf",
        "direct": "local"
    },
    "save_config_path": "D:/Tools/sing-box/profile/config.json",
    "auto_backup": false,
    "exlude_protocol":"ssr"
}
```
订阅 url 支持设置机场订阅链接以及本地文件路径。本地文件比如txt文件，需要在文件中每行一个添加单节点分享链接，比如ss://abcdefg（非订阅链接）。

订阅 tag 会被使用在 config模板文件 中，具体使用方法可以查看下方的 config模板 部分。

enabled：非必需。将其设置为false时，此订阅会被忽略。

prefix：非必需。设置自定义前缀，前缀会添加到对应节点名称前。如果没有设置，则不添加前缀。

![Snipaste_2023-05-02_12-53-27](https://user-images.githubusercontent.com/21310130/235582317-6bb3d0a6-916f-445f-999b-f17b3db41eea.png)
 
 auto_set_outbounds_dns：非必需。
 - 包含 proxy 和 direct 设置项。
 - proxy 和 direct 应该设置为 config 模板文件中存在的 dns server 的 tag。
 - 设置此项后，脚本会自动适配 路由规则 到 dns规则。
 - 将路由规则中 direct 出站 的 dns server 设置为选项中指定的 direct 出站。
 - 将路由规则中需要代理的 出站 设置为对应的 proxy 出站，脚本会自动创建对应出站的 dns server，以 proxy 设置项指定的 dns server 为模板。
 
 save_config_path：必需。设置生成的配置文件路径。
 
 auto_backup：非必需。
 - 设置为true时，脚本会将当前使用的sing-box配置文件更名为 原文件名称.当前时间.bak 进行备份，避免生成错误的配置文件后无法挽回。
 
 exlude_protocol：非必需。
  - 设置不解析的协议，多个使用英文逗号分隔，比如ssr,vmess。
  - 使用此设置中的协议的分享链接会被忽略。
  - sing-box release中的程序没有支持ssr（需要自己添加参数构建），所以此设置可能有用。
# config模板文件
脚本会在 config_template 目录下查找 json 模板文件，脚本运行时可以选择使用的模板文件。

比如目录下存在 tun.json 和 socks.json 两个模板文件。

![Snipaste_2023-03-24_22-16-49](https://user-images.githubusercontent.com/21310130/227548643-ffbf3825-9304-4df7-9b65-82a935227aef.png)

脚本不会检查模板文件的正确性，模板文件不正确会出现错误并无法运行脚本。

目录下自带有一个模板，根据需要修改（必须修改）。
```json
{
  "dns": {
    "servers": [
      {
        "tag": "remote_cf",
        "address": "https://1.0.0.1/dns-query",
        "strategy": "prefer_ipv4"
      },
      {
        "tag": "nodedns",
        "address": "https://doh.pub/dns-query",
        "address_resolver": "local",
        "address_strategy": "prefer_ipv4",
        "strategy": "prefer_ipv4",
        "detour": "direct"
      },
      {
        "tag": "local",
        "address": "114.114.114.114",//这里建议设置为本地上游路由器地址
        "detour": "direct"
      },
      {
        "tag": "block",
        "address": "rcode://success"
      }
    ],
    "rules": [
      {//新版sing-box支持的功能，添加此规则可以避免节点服务器域名解析可能的死循环问题
        "outbound":[
          "any"
        ],
        "server": "nodedns"
      },
      {
        "geosite": "cn",
        "domain_suffix": [
          "msftconnecttest.com"
        ],
        "server": "local"
      },
      {
        "clash_mode": "direct",
        "server": "local"
      }
    ],
    "strategy": "prefer_ipv4"
  },
  "inbounds": [
    {
      "type": "tun",
      "inet4_address": "172.19.0.1/30",
      "auto_route": true,
      "strict_route": false,
      "sniff": true
    }
  ],
  "outbounds": [
    {
      "tag":"proxy",
      "type":"selector",
      "outbounds":[
        "auto",
        "{all}"//所有订阅所有节点添加到此标记所在位置
      ]
    },
    {
      "tag":"netflix",
      "type":"selector",
      "outbounds":[
        "{机场1}",//订阅tag为 机场1 的节点将添加到此标记所在位置
        "{机场2}"//订阅tag为 机场2 的节点将添加到此标记所在位置
      ],
      "filter":[//过滤节点，按顺序执行
        //如果机场1有节点 美国、台湾ˣ²，机场2有节点 sg高速、新加坡ˣ²，他们共同组成 netflix 组
        {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
        //执行完第一个规则后 netflix 组将剩下 台湾ˣ²、sg高速、新加坡ˣ²
        {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
        //for里面设置为机场1，代表此条规则只对机场1起作用
        //执行完第二个规则后 netflix 组将剩下 sg高速、新加坡ˣ²
      ]
    },
    {
      "tag":"speedtest",
      "type":"selector",
      "outbounds":[
        "direct",
        "proxy"
      ]
    },
    {
      "tag":"auto",
      "type":"urltest",
      "outbounds":[
        "{all}"
      ],
      "url": "http://www.gstatic.com/generate_204",
      "interval": "1m",
      "tolerance": 50
    },
    {
      "type": "direct",
      "tag": "direct"
    },
    {
      "type": "block",
      "tag": "block"
    },
    {
      "type": "dns",
      "tag": "dns-out"
    }
  ],
  "route": {
    "rules": [
      {
        "port": 53,
        "outbound": "dns-out"
      },
      {
        "protocol": "dns",
        "outbound": "dns-out"
      },
      {
        "clash_mode": "direct",
        "outbound": "direct"
      },
      {
        "geoip": [
          "private",
          "cn"
        ],
        "outbound": "direct"
      },
      {
        "geosite": "cn",
        "domain_suffix":[
          "msftconnecttest.com",
          "doppiocdn.com",
          "tpkcz.icu",
          "pixeldrain.com"
        ],
        "outbound": "direct"
      },
      {
        "domain_keyword":[
          "speedtest"
        ],
        "domain_suffix":[
          "cdnst.net",
          "ziffstatic.com"
        ],
        "outbound": "speedtest"
      },
      {
          "geosite":"netflix",
          "outbound":"netflix"
      }
    ],
    "auto_detect_interface": true
  },
  "experimental": {
    "clash_api": {
      "external_controller": "127.0.0.1:9090",
      "external_ui": "ui",
      "default_mode": "rule",
      "store_selected": true
    }
  }
}
```
模板文件基本等同于 sing-box config，不过有一些新的参数，比如 {all}、{机场tag}、filter，所有参数仅在clash_mode的出站方式下才会生效，出站类型为 urltest、selector。
```json
{
  "tag":"proxy",
  "type":"selector",
  "outbounds":[
    "auto",
    "{all}"//所有订阅所有节点添加到此标记所在位置
  ],
  "filter":[
    //此条过滤将会删除 机场1 中包含 ˣ² 的节点
    {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
  ]
},
{
  "tag":"netflix",
  "type":"selector",
  "outbounds":[
    "{机场1}",//订阅tag为 机场1 的节点将添加到此标记所在位置
    "{机场2}"//订阅tag为 机场2 的节点将添加到此标记所在位置
  ],
  "filter":[
    //如果机场1有节点 美国、台湾ˣ²，机场2有节点 sg高速、新加坡ˣ²，他们共同组成 netflix 组
    {"action":"include","keywords":["sg","新加坡","tw","台湾"]},
    //执行完第一个规则后 netflix 组将剩下 台湾ˣ²、sg高速、新加坡ˣ²
    {"action":"exlude","keywords":["ˣ²"],"for":["机场1"]}
    //for里面设置为机场1，代表此条规则只对机场1起作用
    //执行完第二个规则后 netflix 组将剩下 sg高速、新加坡ˣ²
  ]
}
```
- {all}：表示所有订阅中的所有节点。脚本会将所有节点添加到有此标识的 outbounds 中。

- {机场tag}：在 providers.json 中设置的机场 tag 可以用于此处，代表此订阅中的所有节点。

- filter：非必需。节点过滤，为一个数组对象，可以添加任意条规则，格式为:
```json
"filter":[
    {"action":"include","keywords":["保留关键字1","保留关键字2"]},
    {"action":"exlude","keywords":["排除关键字1","排除关键字2"],"for":["机场1tag","机场2tag"]}
  ]
```
- **关键字大小写敏感**

- include：后面添加要保留的关键字，名称中包含这些关键字的节点都将被保留，其他节点会被删除。

- exlude：后面添加要排除的关键字，名称中包含这些关键字的节点都将被删除，其他节点会被保留。

- for：非必需。设置机场tag，可以多个，表示此规则只对指定的机场起作用，其他机场会忽略这个规则。

多个规则会按顺序执行过滤。

<details><summary><b>效果参考</b></summary>

<p>

具体效果根据个人的出站及规则设置决定。
</p>
<p>

![Snipaste_2023-03-24_23-54-45](https://user-images.githubusercontent.com/21310130/227577941-01c80cfc-1cd9-4f95-a709-f5442a2a2058.png)

![Snipaste_2023-03-24_23-55-24](https://user-images.githubusercontent.com/21310130/227577968-6747c7aa-db61-4f6c-b7cc-e3802e34cc3d.png)    
</p>
</details>

# 感谢
- [sing-box](https://github.com/SagerNet/sing-box)
- [yacd](https://github.com/haishanh/yacd)
- [clash](https://github.com/Dreamacro/clash)

部分协议解析参考了[convert2clash](https://github.com/waited33/convert2clash)
