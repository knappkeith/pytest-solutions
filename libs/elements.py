from requests_wrapper import CeElementRequests

class QuickBooksDesktop(CeElementRequests):
    element_url = "hubs/finance"

    def __init__(self, *args, **kwargs):
        super(QuickBooksDesktop, self).__init__(*args, **kwargs)

    def send_request(self, resource_url, *args, **kwargs):
        url = [self.element_url, resource_url]
        return super(QuickBooksDesktop, self).send_request(url_path=url, *args, **kwargs)


class DynamicsCRM(CeElementRequests):
    element_url = "hubs/crm"

    def __init__(self, *args, **kwargs):
        super(DynamicsCRM, self).__init__(*args, **kwargs)

    def send_request(self, resource_url, *args, **kwargs):
        url = [self.element_url, resource_url]
        return super(DynamicsCRM, self).send_request(url_path=url, *args, **kwargs)