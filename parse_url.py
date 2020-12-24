import requests
from retrying import retry

headers_default = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}


# 内部发送请求方法
@retry(stop_max_attempt_number=3)  # 允许重试的最大次数为3
def _parse_url(url, method, data, headers):
    if method == "POST":
        response = requests.post(url, data=data, headers=headers, timeout=3)
    else:
        response = requests.get(url, headers=headers, timeout=3)
    assert response.status_code == 200
    return response.content.decode()


# 发送请求，获取响应，并捕获异常
def parse_url(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = headers_default
    try:
        html_str = _parse_url(url, method, data, headers)
    except:
        html_str = None

    return html_str


if __name__ == '__main__':
    url = "www.baidu.com"  # 测试重试机制
    print(parse_url(url))
