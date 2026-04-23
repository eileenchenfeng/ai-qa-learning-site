import json
import os
import sys
from io import open

def patch_file(md_file):
    # 我们直接写一个临时的脚本把 wechat_ready.html 覆盖，然后调 wx api push
    html_content = open(md_file, 'r', encoding='utf-8').read()
    with open('output/wechat_ready.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("wechat_ready.html patched")

if __name__ == '__main__':
    patch_file('AI_Builders_Digest_ZH_2026-04-23_styled.md')
