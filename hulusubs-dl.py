#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib3
import re
import os
import sys
import xml.etree.ElementTree as ET

# check command line arguments
is_srt = True
args = sys.argv
if len(args) > 1:
  if args[1] == '-v' or args[1] == '--vtt':
    is_srt = False

# prompt instruction
print('Copy the text below and paste it to console of your browser to get Content ID:')
print('------------------------------------------------------------------------------')
print('var x=new XMLHttpRequest;x.open("GET","https://discover.hulu.com/content/v4/entity/deeplink?entity_id="+window.location.href.split("/").pop(),!1),x.withCredentials=!0,x.send(null),JSON.parse(x.responseText)["entity"]["bundle"]["eab_id"].split("::")[2];')
print('------------------------------------------------------------------------------')
content_id = input('Enter Content ID: ')

# process
http = urllib3.PoolManager()
r = http.request('GET', f'https://www.hulu.com/captions.xml?content_id={content_id}')
root = ET.fromstring(r.data.decode('utf-8'))
ens = root.findall('./en')
if len(ens) > 0:
  vtt_url = ens[0].text.replace('captions', 'captions_webvtt').replace('.smi', '.vtt')
  r = http.request('GET', vtt_url)
  with open(f'{content_id}.vtt', "w") as vtt_file:
    vtt_file.write(r.data.decode('utf-8'))
  if is_srt:
    with open(f'{content_id}.vtt', 'r+') as read_file:
      lines = read_file.readlines()
      lines.pop()
      new_line_count = 0
      for i, num in enumerate(lines):
        if num == '\n':
          new_line_count += 1
          lines[i] = str(new_line_count)
      read_file.seek(0)
      for line in lines:
        final_line = str(line).replace('WEBVTT\n','').replace('--&gt;', '-->').replace('</p></body></html>', '').replace('.', ',')
        read_file.write(final_line + '\n')
    try:
      os.rename(f'{content_id}.vtt', f'{content_id}.srt')
    except Exception as error:
      print('[Error] Failed to rename file.')
      print(error)
      exit
    print(f'Succeeded in downloading `{content_id}.srt`.')
  else:
    print(f'Succeeded in downloading `{content_id}.vtt`.')
else:
  print('[Error] There is no subtitle in this video.')