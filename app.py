from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)


def validate_url(url):
    if not re.match(r'http(s)?://', url):
        url = 'http://' + url
    return url


def check_keyword(url, keywords):
    try:
        response = requests.get(url)
        status_code = response.status_code
        keyword_found = False
        if status_code == 200:
            content = response.text.lower()  # Convert content to lowercase
            # print("Content for URL", url, ":", content)  # Debug statement
            for keyword in keywords:
                keyword = keyword.strip().lower()  # Convert keyword to lowercase
                print("Checking keyword:", keyword)  # Debug statement
                if keyword in content:
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
    app.run(debug=True)
