import pytest

ELEMENT_CONFIG = {
    "quickbooks_desktop": {
        "user_secret": "gS9xXNOSrebnb0BS956HWNUHMw+iaeHEx1PoMc/Ql9Q=",
        "org_secret": "89341d5d002f3091e5cd5876d7ed8ff0",
        "element_token": "Fa8gVtxDUWp4NJ9VFHQwAaYassdiCFcqw271upqDpgY=",
        "base_url": "https://console.cloud-elements.com/elements"
    },
    "dynamics_crm": {
        "user_secret": "gS9xXNOSrebnb0BS956HWNUHMw+iaeHEx1PoMc/Ql9Q=",
        "org_secret": "89341d5d002f3091e5cd5876d7ed8ff0",
        "element_token": "XuWtBUGuRQiJPl5bIXVaMxcnStWWo/A5udKPj67VTNE=",
        "base_url": "https://console.cloud-elements.com/elements"
    }
}

def test_get_invoices(quickbooks_desktop_element):
    param = {
        'where': "RefNumber='71053'"
    }
    quickbooks_desktop_element.send_request(
        method='get',
        resource_url='invoices',
        params=param)
    quickbooks_desktop_element.print_my_last()
    assert False

def test_get_invoices(dynamics_crm_element):
    param = {
        'where': "statecode='0'"
    }
    dynamics_crm_element.send_request(
        method='get',
        resource_url='salesorders',
        params=param)
    dynamics_crm_element.print_my_last()
    assert False
