import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def check_keyword(url, keywords):
    try:
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

        return {'url': url, 'status_code': status_code, 'keyword_found': keyword_found}

    except requests.exceptions.RequestException as e:
        return {'url': url, 'status_code': str(e), 'keyword_found': False}

def crawl_and_check_keywords(url, keywords, depth):
    visited_links = set()
    results = []

    def crawl(url, current_depth):
        if current_depth > depth or url in visited_links:
            return
        print(url)
        visited_links.add(url)

        result = check_keyword(url, keywords)
        results.append(result)

        if result['status_code'] == 200:
            try:
                response = requests.get(url, allow_redirects=True, verify=True, timeout=30, headers={
                                        'User-Agent': 'Mozilla/5.0'}, stream=True)
                content = response.text.lower()  # Convert content to lowercase
                soup = BeautifulSoup(content, 'html.parser')
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if href.startswith('#'):  # ignore anchor links
                        continue
                    full_url = urljoin(url, href)
                    crawl(full_url, current_depth + 1)
            except requests.exceptions.RequestException:
                pass

    crawl(url, 0)
    return results

results = crawl_and_check_keywords('https://securin.io', ['vulnerability', 'exploit'], 0)
for result in results:
    print(result)



 <!-- <script>
    $(document).ready(function () {
      $("#urlForm").submit(function (event) {
        event.preventDefault();
        var formData = $(this).serializeArray();
        var urls = formData[0].value.trim().split('\n');
        // console.log(url);
        var keywords = formData[1].value.trim();
        var depth = formData[2].value;
        var serialNumber = 1; // Initialize serial number
        var allResults = [];

        var eventSource = new EventSource(`/stream?url=${url}&keywords=${keywords}&depth=${depth}`);
        eventSource.onmessage = function (event) {
          var result = JSON.parse(event.data);
          if (result.done) {
            eventSource.close();
            $("#downloadExcel").show();
            return;
          }

          var websiteAvailable = result.status_code === 200 ? "Yes" : "No";
          var keywordPresent = result.keyword_found ? "Yes" : "No";
          var comments = result.keyword_found ? "Keyword found" : "Keyword not found";

          $("#resultsBody").append(
            "<tr><td>" +
              serialNumber++ +
              "</td><td><a href='" +
              result.url +
              "' target='_blank'>" +
              result.url +
              "</a></td><td>" +
              websiteAvailable +
              "</td><td>" +
              keywordPresent +
              "</td><td>" +
              comments +
              "</td></tr>"
          );

          allResults.push({
            "Sl No": serialNumber - 1,
            Website: result.url,
            "Website Available": websiteAvailable,
            "Keyword Present": keywordPresent,
            Comments: comments,
          });

          // Scroll to the bottom of the page
          $("html, body").scrollTop($(document).height());
        };

        // Function to get status message based on status code
        function getStatusMessage(statusCode) {
          switch (statusCode) {
            case 400:
              return "Bad Request: The server could not understand the request due to invalid syntax.";
            case 401:
              return "Unauthorized: The client must authenticate itself to get the requested response.";
            case 403:
              return "Forbidden: The server understood the request, but refuses to authorize it.";
            case 404:
              return "Not Found: The server has not found anything matching the requested URL.";
            case 500:
              return "Internal Server Error: The server encountered an unexpected condition that prevented it from fulfilling the request.";
            default:
              return "Status Code: " + statusCode;
          }
        }

        // Download Excel
        $("#downloadExcel").click(function () {
          const wb = XLSX.utils.book_new();
          wb.Props = {
            Title: "URL Checker Results",
            Author: "Your Name",
            CreatedDate: new Date(),
          };
          wb.SheetNames.push("Results");
          const ws = XLSX.utils.json_to_sheet(allResults);
          wb.Sheets["Results"] = ws;
          const wbout = XLSX.write(wb, { bookType: "xlsx", type: "binary" });

          function s2ab(s) {
            var buf = new ArrayBuffer(s.length);
            var view = new Uint8Array(buf);
            for (var i = 0; i < s.length; i++) view[i] = s.charCodeAt(i) & 0xff;
            return buf;
          }

          saveAs(
            new Blob([s2ab(wbout)], { type: "application/octet-stream" }),
            "url_checker_results.xlsx"
          );
        });
      });
    });
  </script> -->