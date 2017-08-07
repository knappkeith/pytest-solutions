from libs.requests_wrapper import CeElementRequests

class QuickBooksDesktop(CeElementRequests):
    element_url = "hubs/finance"
    sales_order_url = "salesorder"

    def __init__(self, *args, **kwargs):
        super(QuickBooksDesktop, self).__init__(*args, **kwargs)

    def send_request(self, resource_url, *args, **kwargs):
        url = [element_url, resource_url]
        return super(QuickBooksDesktop, self).send_request(url_path=url, *args, **kwargs)


''' PROD
        user_secret="gS9xXNOSrebnb0BS956HWNUHMw+iaeHEx1PoMc/Ql9Q="
        org_secret="89341d5d002f3091e5cd5876d7ed8ff0"
        token="Fa8gVtxDUWp4NJ9VFHQwAaYassdiCFcqw271upqDpgY="
        base_url="https://console.cloud-elements.com/elements"
'''