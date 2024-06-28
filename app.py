from flask import Flask, render_template, request, Response, stream_with_context
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import json

app = Flask(__name__)

def validate_url(url):
    if not re.match(r'http(s)?://', url):
        url = 'https://' + url
    return url

def check_keyword(url, keywords):
    try:
        response = requests.get(url, allow_redirects=True, verify=True, timeout=30, headers={
                                'User-Agent': 'Mozilla/5.0'}, stream=True)
        status_code = response.status_code
        keyword_found = False

        if status_code == 200:
            content = response.text.lower()
            for keyword in keywords:
                if keyword.strip().lower() in content:
                    keyword_found = True
                    break

        return {'url': url, 'status_code': status_code, 'keyword_found': keyword_found}

    except requests.exceptions.RequestException as e:
        return {'url': url, 'status_code': str(e), 'keyword_found': False}

def crawl_and_check_keywords(url, keywords, depth):
    visited_links = set()
    results = []

    def crawl(url, current_depth):
        if current_depth > depth or url in visited_links:
            return
        visited_links.add(url)

        result = check_keyword(url, keywords)
        results.append(result)
        yield result

        if result['status_code'] == 200 and current_depth < depth:
            try:
                response = requests.get(url, allow_redirects=True, verify=True, timeout=30, headers={
                                        'User-Agent': 'Mozilla/5.0'}, stream=True)
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('#') or href.startswith('mailto:'):
                        continue
                    full_url = urljoin(url, href)
                    if full_url not in visited_links:
                        yield from crawl(full_url, current_depth + 1)
            except requests.exceptions.RequestException:
                pass

    for item in crawl(url, 0):
        yield item
    yield {'done': True}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = validate_url(request.form.get('url', '').strip())
        keywords = request.form.get('keyword', '').split(',')
        depth = int(request.form.get('depth'))

        def generate():
            for result in crawl_and_check_keywords(url, keywords, depth):
                yield f"data: {json.dumps(result)}\n\n"

        return Response(stream_with_context(generate()), content_type='text/event-stream')
    return render_template('index.html')

@app.route('/stream')
def stream():
    url = validate_url(request.args.get('url', '').strip())
    keywords = request.args.get('keywords', '').split(',')
    depth = int(request.args.get('depth'))

    def generate():
        for result in crawl_and_check_keywords(url, keywords, depth):
            yield f"data: {json.dumps(result)}\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
