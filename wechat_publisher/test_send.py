import os
import json
import urllib.request
import urllib.parse
from dotenv import load_dotenv
load_dotenv('../.env')

appid = os.environ.get('WECHAT_APPID')
secret = os.environ.get('WECHAT_APPSECRET')

url = 'https://api.weixin.qq.com/cgi-bin/stable_token'
post_data = {'grant_type': 'client_credential', 'appid': appid, 'secret': secret}
req = urllib.request.Request(url, data=json.dumps(post_data).encode('utf-8'))
req.add_header('Content-Type', 'application/json')
resp = urllib.request.urlopen(req).read().decode('utf-8')
data = json.loads(resp)
token = data.get('access_token')

# 覆盖 HTML 文件
html_content = open('AI_Builders_Digest_ZH_2026-04-23_styled.md', 'r', encoding='utf-8').read()
with open('output/wechat_ready.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# 读取 state.json 里的图片 media id
with open('state.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
thumb_media_id = state.get('thumb_media_id')

# 创建草稿
draft_data = {
    'articles': [
        {
            'title': 'AI Builders Digest | 2026-04-23',
            'author': '陈凤',
            'digest': '企业落地Agent、CI并行化、OpenClaw架构更新与个人的Agent数字分身...',
            'content': html_content,
            'content_source_url': 'https://github.com/zarazhangrui/follow-builders',
            'thumb_media_id': thumb_media_id,
            'need_open_comment': 0,
            'only_fans_can_comment': 0
        }
    ]
}

draft_url = f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}'
req = urllib.request.Request(draft_url, data=json.dumps(draft_data, ensure_ascii=False).encode('utf-8'))
req.add_header('Content-Type', 'application/json')
res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))

print('draft_res:', res)

if 'media_id' in res:
    state['draft_media_id'] = res['media_id']
    with open('state.json', 'w') as f:
        json.dump(state, f)
        
    # 获取草稿列表拿链接
    list_url = f'https://api.weixin.qq.com/cgi-bin/draft/batchget?access_token={token}'
    list_data = {'offset': 0, 'count': 1, 'no_content': 0}
    req_list = urllib.request.Request(list_url, data=json.dumps(list_data).encode('utf-8'))
    req_list.add_header('Content-Type', 'application/json')
    list_res = json.loads(urllib.request.urlopen(req_list).read().decode('utf-8'))

    if 'item' in list_res and len(list_res['item']) > 0:
        print('Draft URL:', list_res['item'][0]['content']['news_item'][0]['url'])
