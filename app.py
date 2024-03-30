from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse, urljoin

app = Flask(__name__)


def validate_url(url):
    if not re.match(r'http(s)?://', url):
        url = 'https://' + url
    return url


def check_keyword(url, keywords, crawl=False, visited_links=None):
    try:
        if visited_links is None:
            visited_links = set()

        response = requests.get(url, allow_redirects=True, verify=True, timeout=30, headers={
                                'User-Agent': 'Mozilla/5.0'}, stream=True)
        status_code = response.status_code
        keyword_found = False

        if status_code == 200:
            content = response.text.lower()  # Convert content to lowercase
            for keyword in keywords:
                keyword = keyword.strip().lower()  # Convert keyword to lowercase
                if keyword in content:
                    keyword_found = True
                    break

            if crawl:
                soup = BeautifulSoup(content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('#'):  # ignore anchor links
                        continue
                    full_url = urljoin(url, href)
                    if full_url not in visited_links:
                        visited_links.add(full_url)
                        found = check_keyword(
                            full_url, keywords, crawl=True, visited_links=visited_links)
                        if found['keyword_found']:
                            keyword_found = True
                            break

        return {'status_code': status_code, 'keyword_found': keyword_found}

    except requests.exceptions.RequestException as e:
        return {'status_code': str(e), 'keyword_found': False}


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        urls = request.form.get('url', '').split('\n')
        keywords = request.form.get('keyword', '').split(',')
        print("Received URLs:", urls)
        print("Received Keywords:", keywords)  # Print received keywords
        results = []
        for url in urls:
            url = validate_url(url.strip())
            result = check_keyword(url, keywords)
            results.append({
                'url': url,
                'status_code': result['status_code'],
                'keyword_found': result['keyword_found']
            })
        print(results)
        return jsonify(results)
    return render_template('index.html')


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
