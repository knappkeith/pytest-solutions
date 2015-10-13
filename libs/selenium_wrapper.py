from selenium import webdriver
from libs.timer_laps import LapWatch

ALL_VARS = {
    "hp_url": {
        "dev": "https://hybgui-dev.viawest.net/login/",
        "staging": "https://hybgui-stg.viawest.net/login/",
        "prod": "https://hybridportal.viawest.com/"
    },
    "user_name": {
        "dev": "api_access",
        "staging": "peter.carr",
        "prod": "peter.carr"
    },
    "password": {
        "dev": "qwe45zxc#!",
        "staging": "whoKnowsThe333rdMind",
        "prod": "whoKnowsThe333rdMind"
    },
    "user_name_multi": {
        "dev": "michael.jordan",
        "staging": "peter.carr",
        "prod": "peter.carr"
    },
    "password_multi": {
        "dev": "Passw0rd!",
        "staging": "whoKnowsThe333rdMind",
        "prod": "whoKnowsThe333rdMind"
    },
    "org": {
        "dev": "12346_A",
        "staging": "86533_A",
        "prod": "86533_A"
    },
    "org_multi": {
        "dev": ["85344_a", "85344_B"],
        "staging": ["86533_A"],
        "prod": ["86533_A"]
    },
    "vcd_url": {
        "dev": "https://vcloud-lab.viawest.com/cloud/org/%s/",
        "staging": "https://vcloud-denver.viawest.com/cloud/org/%s/",
        "prod": "https://vcloud-denver.viawest.com/cloud/org/%s/"
    }
}


class BaseWrapper():
    def set_env_var(self, request_object):
        self.env = request_object.config.option.env
        self.vars = {}
        for var in ALL_VARS:
            try:
                self.vars[var] = ALL_VARS[var][self.env]
            except KeyError:
                pass
        for var in self.vars:
            try:
                if request_object.config.option.__dict__[var]:
                    self.vars[var] = request_object.config.option.__dict__[var]
            except KeyError:
                pass


class Selenium_Wrapper_Firefox(BaseWrapper, webdriver.Firefox):
    def __init__(self, *args, **kwargs):
        self.browser_name = 'Firefox'
        self.timer = LapWatch()
        super(Selenium_Wrapper_Firefox, self).__init__(*args, **kwargs)


class Selenium_Wrapper_Chrome(BaseWrapper, webdriver.Chrome):
    def __init__(self, *args, **kwargs):
        self.browser_name = 'Chrome'
        self.timer = LapWatch()
        super(Selenium_Wrapper_Chrome, self).__init__(*args, **kwargs)


class Selenium_Wrapper_PhantomJS(BaseWrapper, webdriver.PhantomJS):
    def __init__(self, *args, **kwargs):
        self.browser_name = 'PhantomJS'
        self.timer = LapWatch()
        super(Selenium_Wrapper_PhantomJS, self).__init__(*args, **kwargs)
