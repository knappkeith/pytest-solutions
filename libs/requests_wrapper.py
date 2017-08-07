import requests
import json
from url_utils import URL_Utils

class RequestsWrapper(requests.Session):
    def __init__(self):
        self.history = []
        super(RequestsWrapper, self).__init__()

        # `mount` a custom adapter that retries failed connections for HTTP
        # and HTTPS requests.
        self.mount("http://", requests.adapters.HTTPAdapter(max_retries=1))
        self.mount("https://", requests.adapters.HTTPAdapter(max_retries=1))

    def send_request(self, method, url_path, *args, **kwargs):
        if isinstance(url_path, list):
            url_path = "/".join(url_path)
        if "http" in url_path:
            url = url_path
        else:
            url = self._build_url(url_path)
        response = self.request(method.upper(), url, **kwargs)
        self.history.append(response)
        return response

    def _build_url(self, addition_to_path):
        a = self.url.split("/")
        while a[-1] == "":
            a = a[0:-1]
        a.append(addition_to_path)
        return "/".join(a)

    @property
    def last_call(self, attribute=None):
        if not attribute:
            return self.history[-1]
        else:
            return getattr(self.history[-1], attribute)

    def print_my_last(self):
        print self.generate_last_printout()

    def generate_last_printout(self):
        return "\n\n".join([
            self.generate_request_printout(self.last_call),
            self.generate_response_printout(self.last_call)])

    def generate_printout(self, request_obj):
        return "\n\n".join([
            self.generate_request_printout(request_obj),
            self.generate_response_printout(request_obj)])

    def generate_response_printout(self, request_obj, ignore=[]):
        request = request_obj
        output = ["RESPONSE:"]
        if "status" not in ignore:
            output.append("  Status:  {code} - {reason}".format(
                code=request.status_code, reason=request.reason))
        if "headers" not in ignore:
            output = output + self._build_headers(request.headers)
        if "body" not in ignore:
            output = output + self._build_data(request.text)
        return "\n".join(output)

    def generate_request_printout(self, request_obj, ignore=[]):
        request = request_obj.request
        output = ["REQUEST:"]
        output.append("  Method:  {0}".format(request.method))
        output.append("  URL:  {0}".format(request.url))
        if "headers" not in ignore:
            output = output + self._build_headers(request.headers)
        if "body" not in ignore:
            output = output + self._build_data(request.body)
        return "\n".join(output)

    def _build_headers(self, headers):
        heads = ["  Headers:"]
        for header, value in headers.iteritems():
            heads.append("    {0}:  {1}".format(header, value))
        return heads

    def _build_data(self, data):
        rtn_data = ["  Data:"]
        try:
            rtn_data.append(json.dumps(json.loads(data), indent=4))
        except:
            rtn_data.append("    {0}".format(data))
        return rtn_data


class CeElementRequests(RequestsWrapper):
    url_addition = "api-v2"
    instances_url = url_addition + "/instances"

    def __init__(
            self,
            base_url,
            user_secret=None,
            org_secret=None,
            element_token=None,
            user_name=None,
            password=None,
            allow_ssl_error=True):
        super(CeElementRequests, self).__init__()
        self.user_secret = user_secret
        self.org_secret = org_secret
        self.user_name = user_name
        self.password = password
        self.token = element_token
        self.headers['Accept'] = "application/json"
        self.headers['Content-Type'] = "application/json; charset=UTF-8"
        self.headers['X-Requested-With'] = "XMLHttpRequest"
        self.set_auth_header()
        self.url = base_url
        self.global_allow_ssl_error = allow_ssl_error
        self.default_timeout = (3, 90)
        self.instance_id = None
        self.current_user = None

    def send_request(self, *args, **kwargs):
        if isinstance(kwargs.get('url_path', None), list):
            kwargs['url_path'].insert(0, self.url_addition)
        kwargs['timeout'] = kwargs.get('timeout', self.default_timeout)
        kwargs['verify'] = kwargs.get('verify', not self.global_allow_ssl_error)
        return super(CeElementRequests, self).send_request(*args, **kwargs)

    def set_auth_header(self):
        self._set_auth_header(
            user_secret=self.user_secret,
            org_secret=self.org_secret,
            element_token=self.token)

    def delete_me(self):
        if self.instance_id is not None:
            response = self.send_request(
                method='delete',
                url_path="/".join([self.instances_url, str(self.instance_id)]))
            if response.status_code != 200:
                raise Exception(self.generate_last_printout())
            else:
                self.instance_id = None
                self.token = None
                self.set_auth_header()
                return True

    def _set_auth_header(
            self,
            user_secret=None,
            org_secret=None,
            element_token=None):
        self.headers['Authorization'] = self._construct_cloud_elements_header(
            user_secret=user_secret, org_secret=org_secret,
            element_token=element_token)

    def _construct_cloud_elements_header(
            self, user_secret=None, org_secret=None, element_token=None):
        header_array = []
        if user_secret is not None:
            header_array.append("User %s" % user_secret)
        if org_secret is not None:
            header_array.append("Organization %s" % org_secret)
        if element_token is not None:
            header_array.append("Element %s" % element_token)
        return ", ".join(header_array)


# class QuickBooksDesktop(CeElementRequests):
#     element_url = "hubs/finance"
#     sales_order_url = "salesorder"

#     def __init__(self, *args, **kwargs):
#         super(QuickBooksDesktop, self).__init__(*args, **kwargs)

#     def send_request(self, resource_url, *args, **kwargs):
#         url = [self.element_url, resource_url]
#         return super(QuickBooksDesktop, self).send_request(url_path=url, *args, **kwargs)
