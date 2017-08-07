import requests
import pytest
import json

class CloudElementsElementRequest(requests.Session):
    def __init__(
            self,
            base_url,
            user_secret,
            org_secret,
            element_token,
            *args, **kwargs):
        
        super(CloudElementsElementRequest, self).__init__(*args, **kwargs)
        
        self.base_url = base_url
        self.history = []
        self.user_secret = user_secret
        self.org_secret = org_secret
        self.element_token = element_token
        self.headers['Accept'] = 'application/json'
        self.admin_auth = self._build_auth_header(user=user_secret, org=org_secret)
        self.element_auth = self._build_auth_header(user=user_secret, org=org_secret, token=element_token)
        self.headers['Authorization'] = self.element_auth

    def _build_auth_header(self, user, org, token=None):
        items = ["User {user}", "Organization {org}"]
        if token is not None:
            items.append("Element {element}".format(element=token))
        return ", ".join(items).format(user=user, org=org)

    def send_request(self, method, resource, *args, **kwargs):
        response = self.request(method.upper(), self.base_url.format(resource=resource), **kwargs)
        self.history.append(response)
        return response


def compare_json(left_side, right_side, root_path='ROOT', default_list_sort_key='name'):
    
    # recursive function to do actual comparison
    def actual_compare(left, right, list_sort_key, path='ROOT'):
        if left == right:
            return
        
        # sort and verify ARRAY
        if type(left) == list:
            if len(left) > len(right):
                differences.append((
                    'unmatched length',
                    len(left),
                    ">",
                    len(right),
                    path))
            if len(right) > len(left):
                differences.append((
                    'unmatched length',
                    len(left),
                    "<",
                    len(right),
                    path))
            if isinstance(left[0], dict):
                if list_sort_key in left[0].keys():
                    sort_key = list_sort_key
                else:
                    sort_key = left[0].keys()[0]
                differences.append((
                    'list sort key',
                    sort_key,
                    "",
                    "",
                    path))
                left_sorted = sorted(left, key=lambda x: x[sort_key])
                left_names = [x[sort_key].upper() for x in left_sorted]
                right_sorted = sorted(right, key=lambda x: x[sort_key])
                right_names = [x[sort_key].upper() for x in right_sorted]
                for l_name in left_names:
                    if l_name not in right_names:
                        print "{} not in Right".format(l_name)
                for r_name in right_names:
                    if r_name not in left_names:
                        print "{} not in Right".format(r_name)

            else:
                left_sorted = sorted(left)
                right_sorted = sorted(right)
        
        # Sort and Verify DICTIONARY
        elif type(left) == dict:
            left_keys = sorted(left.keys())
            right_keys = sorted(right.keys())
            if left_keys != right_keys:
                differences.append((
                    'unmatched keys',
                    sorted(left.keys()),
                    "!=",
                    sorted(right.keys()),
                    path))
                if len(left_keys) != len(right_keys):
                    if len(left_keys) > len(right_keys):
                        rm_keys = [x for x in left_keys if x not in right_keys]
                    elif len(left_keys) < len(right_keys):
                        rm_keys = [x for x in right_keys if x not in left_keys]
                    for rm_key in rm_keys:
                        differences.append((
                            'removing key',
                            rm_key,
                            "",
                            "",
                            path))
                        try:
                            del left[rm_key]
                        except:
                            pass
                        try:
                            del right[rm_key]
                        except:
                            pass
            left_sorted = sorted(left.iteritems())
            right_sorted = sorted(right.iteritems())
        
        # Verify STRING
        elif type(left) == str or type(left) == unicode:
            differences.append((
                'not equal',
                left,
                "!=",
                right,
                path))
            return
        
        # Unknown Type?
        else:
            differences.append((
                'unknown type',
                type(left),
                "not in",
                "[list, dict, str]",
                path))
            return 

        # return if equal after sorting
        if left_sorted == right_sorted:
            return

        # Check each value
        for index in range(0, len(left_sorted)):
            if left_sorted[index] != right_sorted[index]:
                if isinstance(left_sorted[index], tuple):
                    if isinstance(left_sorted[index][1], dict):
                        actual_compare(
                            left=left_sorted[index][1],
                            right=right_sorted[index][1],
                            path="{}>{}".format(path, left_sorted[index][0]),
                            list_sort_key=list_sort_key)
                    elif  isinstance(left_sorted[index][1], list):
                        if index > len(left_sorted) or index > len(right_sorted):
                            pass
                        else:
                            actual_compare(
                                left=left_sorted[index][1],
                                right=right_sorted[index][1],
                                path="{}>{}".format(path, left_sorted[index][0]),
                                list_sort_key=list_sort_key)
                    else:
                        differences.append((
                            'not equal',
                            left_sorted[index],
                            "!=",
                            right_sorted[index],
                            "{}>{}".format(path, left_sorted[index][0])))
                else:
                    actual_compare(
                        left=left_sorted[index],
                        right=right_sorted[index],
                        path="{}>{}".format(path, index),
                        list_sort_key=list_sort_key)
            else:
                pass

    differences = []
    actual_compare(
        left=left_side,
        right=right_side,
        path=root_path,
        list_sort_key=default_list_sort_key)
    return differences


# @pytest.fixture()
# def new():
#     db_new = CloudElementsElementRequest(
#         base_url="https://snapshot.cloud-elements.com/elements/api-v2/hubs/documents/{resource}",
#         user_secret="wUA03uERFYxWMb+1E1ncNh0B9jEZJ8YOUlgJDOeFPrE=",
#         org_secret="bc15df3fd4922fd66879960cd69539eb",
#         element_token="q0qtvwD9hvSGSM+Jz9MbDYnEucgUB4G/RM7vaXLM0Lg=")
#     return db_new

@pytest.fixture()
def new():
    db_new = CloudElementsElementRequest(
        base_url="https://console.cloud-elements.com/elements/api-v2/hubs/documents/{resource}",
        user_secret="MaDbkG4uvwgD2zgPrdlnENXejNwBsbgpIbsbidxLm2E=",
        org_secret="fcf15248575c541a640a5828d77a6ae8",
        element_token="+Ngkf18GDusProcNn48NLy/uJ5cocf06HmQAFzHemOs=")
    return db_new


@pytest.fixture()
def old():
    db_old = CloudElementsElementRequest(
        base_url="https://console.cloud-elements.com/elements/api-v2/hubs/documents/{resource}",
        user_secret="MaDbkG4uvwgD2zgPrdlnENXejNwBsbgpIbsbidxLm2E=",
        org_secret="fcf15248575c541a640a5828d77a6ae8",
        element_token="ZJEHPBLDNuAq2Dwh6VM/BM+QqXF/NaoN+s8Ptwai3NU=")
    return db_old

FILE_ID = "%252F2015%2Bfederal%2Btax%2Breturn.pdf"
FILE_PATH = "/2015 federal tax return.pdf"
FILE_PATH_ALT = "/Profile Pictures/2015 federal tax return_new.pdf"

FILE_ID_2 = "%252Fprofile%2Bpictures%252Fdeutschland%2B-%2Bheidelberg%2B-%2Bschloss.jpg"
FILE_PATH_2 = "/Profile Pictures/Deutschland - Heidelberg - Schloss.JPG"

FOLDER_ID = "%252FProfile%2BPictures"
FOLDER_PATH = "/Profile Pictures"

FOLDER_ID_2 = "%252FScreenshots"
FOLDER_PATH_2 = "/Screenshots"

# @pytest.mark.skipif(True, reason="because")
@pytest.mark.parametrize(('method', 'endpoint', 'my_params', 'my_data'),[

    # ("get", "/folders/{id}/metadata".format(id=FOLDER_ID), None, None),
    # ("get", "/storage", None, None),
    # ("get", "/files/{id}/links".format(id=FILE_ID), None, None),
    # ("get", "/files/links", {'path': FILE_PATH}, None),
    # ("get", "/files/{id}/metadata".format(id=FILE_ID), None, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), None, None),
    # ("get", "/files/{id}".format(id=FILE_ID), None, None),
    # ("get", "/folders/contents", {'path': FOLDER_PATH}, None),
    # ("get", "/files", {'path': FILE_PATH}, None),
    # ("get", "/folders/metadata", {'path': FOLDER_PATH}, None),
    # ("get", "/search", {'text': 'tax return'}, None),
    # ("get", "/ping", None, None),
    # ("get", "/files/metadata", {'path': FILE_PATH}, None),

    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), {'fetchTags': True}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), {'fetchTags': False}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), {'fetchTags': 'true'}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), {'fetchTags': 'false'}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID), {'fetchTags': 'poop'}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID_2), {'pageSize': 2}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID_2), {'pageSize': 2, 'page': 1}, None),
    # ("get", "/folders/{id}/contents".format(id=FOLDER_ID_2), {'pageSize': 1000}, None),
    # ("patch", "/folders/{id}/metadata".format(id=FOLDER_ID), None, {'tags':['hi']}),
    # ("patch", "/files/{id}/metadata".format(id=FILE_ID), None, {'tags':['hello']}),
    # ("patch", "/folders/metadata", {'path': FOLDER_PATH}, {'tags':['hi']}),
    # ("patch", "/files/metadata", {'path': FILE_PATH}, {'tags':['hello']}),
    ("patch", "/files/metadata", {'path': FILE_PATH}, {'path': FILE_PATH_ALT})
    ], ids=str)
def test_basic_response_compare(new, old, method, endpoint, my_params, my_data):
    isJson = True
    try:
        new_obj = new.send_request(method, resource=endpoint, params=my_params, json=my_data)
        new_response = new_obj.json()
    except ValueError:
        new_response = new.send_request(method, resource=endpoint, params=my_params, json=my_data)
        isJson = False
    try:
        # old_obj = old.send_request(method, resource=endpoint, params=my_params, json=my_data)
        old_obj = old.send_request(method, resource=endpoint, params=my_data, json=my_params)
        old_response = old_obj.json()
    except ValueError:
        old_response = old.send_request(method, resource=endpoint, params=my_params, json=my_data)
        isJson = False
    if isJson:
        printed_new = json.dumps(new_response, indent=2)
        printed_old = json.dumps(old_response, indent=2)

        try:
            diff = compare_json(new_response, old_response, "GET {}".format(endpoint))
            # diff = [x for x in diff if x[0] == 'not equal']
            for item in diff:
                print str(item)
        except:
            print "NEW: ({})".format(new_obj.status_code)
            print printed_new
            print "OLD: ({})".format(old_obj.status_code)
            print printed_old
            raise

        if old_obj.status_code != 200 or new_obj.status_code != 200:
            print "NEW: ({})".format(new_obj.status_code)
            print printed_new
            print "OLD: ({})".format(old_obj.status_code)
            print printed_old
            assert False

        if len(diff) != 0:
            assert False
    else:
        assert new_response.text == old_response.text

@pytest.mark.skipif(True, reason="because")
@pytest.mark.parametrize(('method', 'endpoint', 'my_params'),[
    ("get", "/folders/{id}/contents".format(id=FOLDER_ID_2), {'pageSize': 1000})
    ], ids=str)
def test_temp(new, old, method, endpoint, my_params):
    new_response = new.send_request(method, resource=endpoint, params=my_params).json()
    old_response = old.send_request(method, resource=endpoint, params=my_params).json()
    
    new_names = [x['name'] for x in new_response]
    old_names = [x['name'] for x in old_response]

    for index in range(0,len(new_response)):
        if new_names[index] == old_names[index]:
            print "{}({}) == {}({})".format(new_names[index], new_response[index]['modifiedDate'], old_names[index], old_response[index]['modifiedDate'])
        else:
            print "{}({}) != {}({})".format(new_names[index], new_response[index]['modifiedDate'], old_names[index], old_response[index]['modifiedDate'])
    assert False
    assert new_names == old_names
    assert False
    for key in new_response[0].keys():
        sort_new = sorted(new_response, key=lambda x: x[key])
        if sort_new == new_response:
            print "worked {}".format(key)
        else:
            print "didn't work {}".format(key)
    assert False