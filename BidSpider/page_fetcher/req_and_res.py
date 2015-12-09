class Request(object):
    def __init__(self, url):
        self.url = url


class Response(object):
    def __init__(self, url, content):
        self.url = url
        self.content = content


class SpiderLabeledRequest(object):
    def __init__(self, spider, request):
        self.spider = spider
        self.request = request

    @property
    def url(self):
        return self.request.url


class SpiderLabeledResponse(object):
    def __init__(self, spider, response):
        self.spider = spider
        self.response = response

    @property
    def url(self):
        return self.response.url

    @property
    def content(self):
        return self.response.content