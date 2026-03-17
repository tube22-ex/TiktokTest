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
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"URL is required")
            return

        try:
            # ブラウザからのアクセスに見せかけるためのヘッダー
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
            }
            # TikTokのページを取得
            response = requests.get(video_url, headers=headers, timeout=10)
            
            # ページ内のソースから "duration":123 を探す
            match = re.search(r'"duration":(\d+)', response.text)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if match:
                duration = int(match.group(1))
                self.wfile.write(json.dumps({'duration': duration}).encode())
            else:
                # 見つからない場合は0を返すかエラーメッセージ
                self.wfile.write(json.dumps({'duration': None, 'error': 'Not found'}).encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())
