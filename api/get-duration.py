from http.server import BaseHTTPRequestHandler
import urllib.parse
import urllib.request
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # URLパラメータの取得
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        video_url = params.get('url', [None])[0]

        if not video_url:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"URL is required")
            return

        try:
            # Python標準のurllibを使用。これなら追加ライブラリ(requests)不要
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }
            req = urllib.request.Request(video_url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
            
            # ソースコードから "duration":数字 を探す
            match = re.search(r'"duration":(\d+)', html)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # CORSエラー防止
            self.end_headers()

            if match:
                duration = int(match.group(1))
                self.wfile.write(json.dumps({'duration': duration}).encode())
            else:
                self.wfile.write(json.dumps({'duration': None, 'error': 'Duration not found in HTML'}).encode())

        except Exception as e:
            # エラー内容をブラウザに返す
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Server Error: {str(e)}".encode())
