import time
import string
import random
import requests


class CloudElementsRequestBin(object):
    url = "http://knappkeith.pythonanywhere.com/"

    def __init__(self, session_name):
        self.session_name = session_name
        self.callback_url = self._build_url(session_name)

    def get_bin(self):
        params = {"returnQueue": True}
        response = requests.request("get", self.callback_url, params=params)
        return response.json()

    def wait_for_request(self, timeout=300):
        response_json = self.get_bin()
        cnt = 0
        while response_json['count'] == 0:
            time.sleep(1)
            response_json = self.get_bin()
            cnt += 1
            if cnt > timeout:
                raise Exception(
                    "No Request was recieved within %d seconds!" % timeout)
        return response_json

    def _build_url(self,
                   addition_to_path):
        a = self.url.split("/")
        while a[-1] == "":
            a = a[0:-1]
        b = addition_to_path.split("/")
        while b[0] == "" and len(b) > 1:
            b = b[1:]
        a.append("/".join(b))
        a.append("")
        return "/".join(a)


class RobotElementRequestBin(CloudElementsRequestBin):
    def __init__(self):
        session_name = self._generate_session_id()
        super(RobotElementRequestBin, self).__init__(session_name=session_name)

    def _generate_session_id(self):
        chars = string.digits + string.ascii_lowercase
        size = 8
        return ''.join(random.choice(chars) for _ in range(size))
