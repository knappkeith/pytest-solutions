from urlparse import urlparse, urlunparse


class URL_Utils(object):
    def __init__(self, base_url):
        self.base_url_parsed = urlparse(base_url)
        self._set_initial_values()

    def _set_initial_values(self):
        self._SCHEME = self.base_url_parsed.scheme
        self._NETLOC = self.base_url_parsed.netloc
        self._PATH = self.base_url_parsed.path
        self._PARAMS = self.base_url_parsed.params
        self._QUERY = self.base_url_parsed.query
        self._FRAGMENT = self.base_url_parsed.fragment
        self._USERNAME = self.base_url_parsed.username
        self._PASSWORD = self.base_url_parsed.password
        self._HOSTNAME = self.base_url_parsed.hostname
        self._PORT = self.base_url_parsed.port
        self.reset_current_values()

    def get_scheme(self):
        return self._SCHEME

    def get_netloc(self):
        return self._NETLOC

    def get_path(self):
        return self._PATH

    def get_params(self):
        return self._PARAMS

    def get_query(self):
        return self._QUERY

    def get_fragments(self):
        return self._FRAGMENT

    def get_username(self):
        return self._USERNAME

    def get_password(self):
        return self._PASSWORD

    def get_hostname(self):
        return self._HOSTNAME

    def get_port(self):
        return self._PORT

    def get_current(self):
        return self._build_current_dictionary()

    def reset_current_values(self):
        self.current_values = self._build_current_dictionary()

    def _build_current_dictionary(self):
        current_parse = {
            'scheme': self._SCHEME,
            'netloc': self._NETLOC,
            'path': self._PATH,
            'params': self._PARAMS,
            'query': self._QUERY,
            'fragment': self._FRAGMENT,
            'username': self._USERNAME,
            'password': self._PASSWORD,
            'hostname': self._HOSTNAME,
            'port': self._PORT
        }
        return current_parse

    def _build_path(self, to_add):
        org_path = self.current_values['path']
        return "/".join([org_path.strip('/'), to_add.strip('/')])

    def build_url(self, add_to_path=None):
        if add_to_path is not None:
            self.current_values['path'] = self._build_path(add_to_path)

        unparsed = self.unparse_url()
        self.reset_current_values()
        return unparsed

    def unparse_url(self):
        return urlunparse(self._build_tuple())

    def _build_tuple(self):
        unparse_array = []
        unparse_array.append(self.current_values['scheme'])
        unparse_array.append(self.current_values['netloc'])
        unparse_array.append(self.current_values['path'])
        unparse_array.append(self.current_values['params'])
        unparse_array.append(self.current_values['query'])
        unparse_array.append(self.current_values['fragment'])
        return tuple(unparse_array)
