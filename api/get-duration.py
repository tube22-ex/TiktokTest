from http.server import BaseHTTPRequestHandler
import urllib.parse
import json
import requests
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        video_url = params.get('url', [None])[0]

        if not video_url:
            self.send_error(400, "URL is required")
            return

        try:
            # TikTokのページをフェッチ（User-Agentを偽装）
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(video_url, headers=headers, timeout=10)
            
            # ページ内のJSONデータからdurationを探す（正規表現）
            # "duration":123 というパターンを抽出
            match = re.search(r'"duration":(\d+)', response.text)
            
            if match:
                duration = int(match.group(1))
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') # CORS許可
                self.end_headers()
                self.wfile.write(json.dumps({'duration': duration}).encode())
            else:
                self.send_error(404, "Duration not found in page")

        except Exception as e:
            self.send_error(500, str(e))
