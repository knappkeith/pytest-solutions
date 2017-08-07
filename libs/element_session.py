from requests_wrapper import SolutionsRequests
from urlparse import urljoin


class ElementSession(SolutionsRequests):
    def __init__(
            self,
            base_url,
            user_name=None,
            password=None,
            org_secret=None,
            user_secret=None,
            element_token=None):
        self.url = urljoin(base_url, self.url_path)
        self.org_secret = org_secret
        self.user_secret = user_secret
        if element_token:
            self.token = element_token
        if user_name and password:
            self.org_secret, self.user_secret = self._get_secrets(
                base_url, user_name, password)
        elif not user_secret or not org_secret:
            raise ValueError(
                "Must provide user name/password or user/org secrets!")
        super(ElementSession, self).__init__()


class NimsoftElement(ElementSession):
    posted_alarms = []
    url_path = "monitoring"
    default_alert = {
            "custom1": "-",
            "origin": "nimsoft-hub-1_hub", 
            "subsystem": "Host", 
            "domain": "nimsoft-hub-1_domain", 
            "hostname": "nimsoft-hub-1", 
            "severity": "information", 
            "hub": "nimsoft-hub-1_hub", 
            "level": 0, 
            "probe": "cdm", 
            "robot": "nimsoft-hub-10000", 
            "nas": "nimsoft-hub-1_hub", 
            "source": "159.203.164.11", 
            "message": ""
        }

    def post_alarm(self, alarm_json):
        response = self.send_request('post', 'alarms', json=alarm_json)
        if response.status_code == 200:
            self.posted_alarms.append(NimsoftAlarm(alarm_json, self))
        else:
            raise Exception(
                "Alarm Creatation failed: %d:%s\n%s" % (
                response.status_code, response.reason, response.text))

    def update_alarm(self, alarm_id, new_level, **kwargs):
        update_json = dict(self.posted_alarms[alarm_id].json)
        try:
            del update_json['custom1']
        except:
            pass
        update_json['level'] = new_level
        for k, v in kwargs.iteritems():
            if update_json.get(i, "notdefined") != "notdefined":
                update_json[k] = v
        response = self.send_request('post', 'alarms', json=update_json)
        if response.status_code != 200:
            raise Exception(
                "Alarm Update failed: %d:%s\n%s" % (
                response.status_code, response.reason, response.text))

    def get_alarm(self, alarm_id):
        params = {'where': 'message=%r' % self.posted_alarms[alarm_id].json['message']}
        response = self.send_request('get', 'alarms', params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                "Error Retrieving Alarm: %d:%s\n%s" % (
                response.status_code, response.reason, response.text))

    def get_basic_alarm(self, message, level):
        a = dict(self.default_alert)
        a['message'] = message
        a['level'] = level
        return a


class NimsoftAlarm(object):
    def __init__(self, org_json, element_session):
        self.json = dict(org_json)
        self._id = None
        self.session = element_session

    @property
    def id(self):
        if self._id is None:
            if self.json['custom1'] != '-':
                self._id = self.json['custom1']
                return self._id
            else:
                params = {'where': 'message=%r' % self.json['message']}
                response = self.session.send_request('get', 'alarms', params=params)
                if response.status_code == 200:
                    self.update(response.json())
                    return self.id
                raise ValueError, "Failed to get response from '/alarms': %d" % response.status_code
        return self._id

    def update(self, new_json):
        if isinstance(new_json, dict):
            self.json = dict(new_json)
        elif isinstance(new_json, list):
            print "JSON is an array!?!?"
            self.json = dict(new_json[0])


        """
        a = NimsoftElement(user_secret="oMIVVEyuzRFP2Spr2OUkCUNlkpDe4vr74KXoLbKV6rA=", org_secret="b97a3d41f474878e93352c2e1886dd61", element_token="uBUa/yRphXWI9JHR7aeQs5h/xRT+i5aX8L2zFSwRgLA=", base_url="https://snapshot.cloud-elements.com/elements/api-v2/hubs/")


        {
            "custom1": "-",
            "origin": "nimsoft-hub-1_hub", 
            "subsystem": "Host", 
            "domain": "nimsoft-hub-1_domain", 
            "hostname": "nimsoft-hub-1", 
            "severity": "information", 
            "hub": "nimsoft-hub-1_hub", 
            "level": 0, 
            "probe": "cdm", 
            "robot": "nimsoft-hub-10000", 
            "nas": "nimsoft-hub-1_hub", 
            "source": "159.203.164.11", 
            "message": "keith-test-228"
        }
        """
