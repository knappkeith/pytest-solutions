import requests
import json
import os
from requests.exceptions import RequestException


class SolutionsRequests(requests.Session):
    def __init__(self):
        self.history = []
        super(SolutionsRequests, self).__init__()
        self.headers['Accept'] = "application/json"
        self.headers['Content-Type'] = "application/json"
        self.headers['Authorization'] = \
            "User {user_secret}, Organization {organization_secret}".format(
                user_secret=self.user_secret, organization_secret=self.org_secret)

    def send_request(self, method, url_path, **kwargs):
        url = self._build_url(url_path)
        response = self.request(method.upper(), url, **kwargs)
        self.history.append(response)
        return response

    def send_page_request(self, method, url_path, **kwargs):
        url = self._build_url(url_path)
        next_page = True
        params = {}
        while next_page:
            response = self.request(method.upper(), url, params=params, **kwargs)
            self.history.append(response)
            yield response.json()
            try:
                params['nextPage'] = response.headers['elements-next-page-token']
            except:
                next_page = False

    def _build_url(self,
                   addition_to_path):
        a = self.url.split("/")
        while a[-1] == "":
            a = a[0:-1]
        b = addition_to_path.split("/")
        while b[0] == "" and len(b) > 1:
            b = b[1:]
        a.append("/".join(b))
        return "/".join(a)

    def print_my_last(self):
        self._print_request_response(self.history[-1])

    def check_response(self,
                       response,
                       status=200,
                       response_body=True,
                       valid_json=True):
        if response.status_code != status:
            raise RequestException(
                "Invalid Response code: %d - %s, expected %d" % (
                    response.status_code,
                    response.reason,
                    status))
        if response.text == "" and response_body:
            raise RequestException("No Response Body found!")
        try:
            response.json()
        except:
            if valid_json:
                raise RequestException("No valid JSON Response Body found!")
        return True

    def _print_request_response(self,
                                request_obj):
        request = request_obj.request
        response = request_obj

        print "\nREQUEST:"
        print "  ".join(["", "Method:", request.method])
        print "  ".join(["", "URL:", request.url])
        print "  ".join(["", "Headers:"])
        for i in request.headers:
            print "  ".join(["", "", i + ":", request.headers[i]])
        print "  ".join(["", "Data:"])
        try:
            print json.dumps(json.loads(request.body), indent=4)
        except:
            print "    %s" % request.body

        print ""
        print "RESPONSE:"
        print "  ".join([
            "",
            "Status:",
            str(response.status_code),
            str(response.reason)])
        print "  ".join(["", "Headers:"])
        for i in response.headers:
            print "  ".join(["", "", i + ":", response.headers[i]])
        print "  ".join(["", "Data:"])
        try:
            print json.dumps(response.json(), indent=2)
        except:
            print "    %s" % response.text

    def _convert_values(self,
                        thing_2_convert):
        """
        This function will go through a JSON object and attempt to convert all
        strings that can be converted to JSON objects
        """
        if isinstance(thing_2_convert, str) or \
                isinstance(thing_2_convert, unicode):
            a = thing_2_convert
            try:
                a = json.loads(thing_2_convert)
            except ValueError as e:
                if 'No JSON object could be decoded' in str(e):
                    pass
                elif 'Extra data:' in str(e):
                    pass
                else:
                    raise
            return a
        elif isinstance(thing_2_convert, list):
            to_return = []
            for i in thing_2_convert:
                to_return.append(self._convert_values(i))
            return to_return
        elif isinstance(thing_2_convert, dict):
            to_return = dict(thing_2_convert)
            try:
                to_return['value'] = self._convert_values(thing_2_convert['value'])
            except:
                pass
            for i in thing_2_convert:
                to_return[i] = self._convert_values(thing_2_convert[i])
            return to_return
        else:
            return thing_2_convert

    def iterate_dict(self,
                     idict,
                     mapping):
        final_mapping = []

        if isinstance(mapping, (str, unicode)):
            mapping = [mapping]

        def get_dict_array():
            rtn_val = idict
            for i in final_mapping:
                if isinstance(rtn_val[i], list):
                    rtn_val = list(rtn_val[i])
                elif isinstance(rtn_val[i], dict):
                    rtn_val = dict(rtn_val[i])
                else:
                    rtn_val = rtn_val[i]
            return rtn_val

        for item in mapping:
            if isinstance(item, (str, int, unicode)):
                final_mapping.append(item)
            elif isinstance(item, tuple):
                dict_list = get_dict_array()
                if isinstance(dict_list, list):
                    index_found = False
                    for index, i in enumerate(dict_list):
                        # if i[item[0]] == item[1]:
                        if self.iterate_dict(i, item[0])[0] == item[1]:
                            final_mapping.append(index)
                            index_found = True
                            break
                    if not index_found:
                        raise ValueError("Unable to locate %r: %r - %r: %r" % (
                            "Key",
                            item[0],
                            "Value",
                            item[1]))
                else:
                    raise TypeError("Invalid Type for lookup: %s \n %s" % (
                        type(dict_list),
                        dict_list))
            else:
                raise TypeError(
                    "Invalid Mapping type: %s must be of type %r" % (
                        item,
                        "str, unicode, int, tuple"))
        return get_dict_array(), final_mapping

    def read_json_file(self,
                       file_path):
        file_path = os.path.expanduser(file_path)
        if not os.path.isfile(file_path):
            raise IOError
        with open(file_path, 'r') as f:
            file_contents = f.read()
        return json.loads(file_contents)


class FormulaEndpoints(SolutionsRequests):
    formula_path = \
        "/formulas"
    formula_instance_path = formula_path + \
        "/instances"
    formula_id_path = formula_path + \
        "/{formula_id}"
    formula_id_instances_path = formula_id_path + \
        "/instances"
    formula_id_instances_id_path = formula_id_instances_path + \
        "/{formula_instance_id}"
    formula_id_instances_id_executions_path = formula_id_instances_id_path + \
        "/executions"
    formula_id_instances_id_executions_id_path = formula_id_instances_id_executions_path + \
        "/{formula_instance_execution_id}"

    def __init__(self,
                 base_url="https://snapshot.cloud-elements.com/elements/api-v2",
                 org_secret="bc15df3fd4922fd66879960cd69539eb",
                 user_secret="wUA03uERFYxWMb+1E1ncNh0B9jEZJ8YOUlgJDOeFPrE="):
        self.url = base_url
        self.org_secret = org_secret
        self.user_secret = user_secret
        super(FormulaEndpoints, self).__init__()
        self.url_vars = {
            "formula_id": None,
            "formula_instance_id": None,
            "formula_instance_execution_id": None
        }

    def get_formula(self,
                     formula_id=None,
                     **kwargs):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        return self.send_request(
            "get",
            self.formula_id_path.format(**url_path_vars))

    def get_formulas(self,
                      **kwargs):
        return self.send_request(
            "get",
            self.formula_path,
            **kwargs)

    def get_formula_instance(self,
                              formula_id=None,
                              instance_id=None):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        if instance_id:
            url_path_vars['formula_instance_id'] = instance_id
        return self.send_request(
            "get",
            self.formula_id_instances_id_path.format(**url_path_vars))

    def get_formula_instances(self,
                               formula_id=None,
                               **kwargs):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        return self.send_request(
            "get",
            self.formula_id_instances_path.format(**url_path_vars),
            **kwargs)

    def get_formula_instance_execution(self,
                                        formula_id=None,
                                        instance_id=None,
                                        execution_id=None):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        if instance_id:
            url_path_vars['formula_instance_id'] = instance_id
        if execution_id:
            url_path_vars['formula_instance_execution_id'] = execution_id
        return self.send_request(
            "get",
            self.formula_id_instances_id_executions_id_path.format(
                **url_path_vars))

    def get_formula_instance_executions(self,
                                         formula_id=None,
                                         instance_id=None,
                                         **kwargs):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        if instance_id:
            url_path_vars['formula_instance_id'] = instance_id
        return self.send_request(
            "get",
            self.formula_id_instances_id_executions_path.format(**url_path_vars),
            **kwargs)

    def post_formula(self,
                      formula_data):
        response = self.send_request(
            'post',
            self.formula_path,
            json=formula_data)
        if self.check_response(response):
            print response.json()['id']
            self.url_vars['formula_id'] = response.json()['id']
        return response

    def post_instance(self,
                      instance_data,
                      formula_id=None):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        response = self.send_request(
            'post',
            self.formula_id_instances_path.format(**url_path_vars),
            json=instance_data)
        if self.check_response(response):
            self.url_vars['formula_instance_id'] = response.json()['id']
        return response

    def delete_formula(self,
                       formula_id=None,
                       **kwargs):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        return self.send_request(
            "delete",
            self.formula_id_path.format(**url_path_vars))

    def delete_formula_instance(self,
                                formula_id=None,
                                instance_id=None):
        url_path_vars = dict(self.url_vars)
        if formula_id:
            url_path_vars['formula_id'] = formula_id
        if instance_id:
            url_path_vars['formula_instance_id'] = instance_id
        return self.send_request(
            "delete",
            self.formula_id_instances_id_path.format(**url_path_vars))

    def _retrieve_ids(self,
                      func,
                      **kwargs):
        return_ids = []
        next_page = True
        params = {}
        while next_page:
            response = func(params=params, **kwargs)
            self.check_response(response)
            for i in response.json():
                return_ids.append(i['id'])
            try:
                params['nextPage'] = response.headers['elements-next-page-token']
            except:
                next_page = False
        return return_ids

    def retrieve_formula_ids(self):
        """
        Returns a list of all the formula IDs
        """
        return self._retrieve_ids(func=self.get_formulas)

    def retrieve_formula_instance_ids(self,
                                       formula_id=None):
        """
        Returns a list of all the formula instance IDs
        """
        return self._retrieve_ids(func=self.get_formula_instances,
                                  formula_id=formula_id)

    def retrieve_formula_instance_executions_ids(self,
                                                  formula_id=None,
                                                  instance_id=None):
        """
        Returns a list of all the formula instance execution IDs
        """
        return self._retrieve_ids(func=self.get_formula_instance_executions,
                                  formula_id=formula_id,
                                  instance_id=instance_id)

    def set_formula_id(self):
        """
        Sets the Class formula ID to the highest numbered formula
        """
        ids = self.retrieve_formula_ids()
        ids.sort()
        try:
            self.url_vars['formula_id'] = ids[-1]
        except IndexError:
            pass

    def set_instance_id(self):
        """
        Sets the Class instance ID to the highest numbered instance
        """
        ids = self.retrieve_formula_instance_ids()
        ids.sort()
        try:
            self.url_vars['formula_instance_id'] = ids[-1]
        except IndexError:
            pass

    def set_execution_id(self):
        """
        Sets the Class execution ID to the highest numbered execution
        """
        ids = self.retrieve_formula_instance_executions_ids()
        ids.sort()
        try:
            self.url_vars['formula_instance_execution_id'] = ids[-1]
        except IndexError:
            pass

    def set_formula(self):
        self.cur_formula = self.get_formula()

    def set_instance(self):
        self.cur_instance = self.get_formula_instance()

    def set_execution(self):
        self.cur_execution = self.get_formula_instance_execution()

    def set_all_url_vars(self):
        """
        Sets the Class IDs to the highest numbered IDs
        """
        self.set_formula_id()
        self.set_instance_id()
        self.set_execution_id()

    def set_all_current(self):
        self.set_formula()
        self.set_instance()
        self.set_execution()

    def get_failed_steps(self,
                         formula_id=None,
                         instance_id=None,
                         execution_id=None):
        if formula_id or instance_id or execution_id:
            wf = self.get_formula(formula_id=formula_id).json()
            execution = self.get_formula_instance_execution(
                formula_id=formula_id,
                instance_id=instance_id,
                execution_id=execution_id).json()
        else:
            if hasattr(self, "cur_formula"):
                wf = self.cur_formula.json()
            else:
                wf = self.get_formula(formula_id=formula_id).json()
            if hasattr(self, "cur_execution"):
                execution = self.cur_execution.json()
            else:
                execution = self.get_formula_instance_execution(
                    formula_id=formula_id,
                    instance_id=instance_id,
                    execution_id=execution_id).json()
        failed_steps = []
        for step in execution['stepExecutions']:
            if step['status'] == "failed":
                temp_step = {
                    "step": self._find_step(wf, step['stepName']),
                    "execution": step
                    }
                failed_steps.append(temp_step)
        return failed_steps

    def _find_step(self,
                   formula_json,
                   step_name):
        for i in formula_json['steps']:
            if i['name'] == step_name:
                return i
        for i in formula_json['triggers']:
            if i['name'] == step_name:
                return i

    def _find_step_execution(self,
                             execution_json,
                             step_name):
        for i in execution_json['stepExecutions']:
            if i['stepName'] == step_name:
                return i

    def my_exec(self,
                search_str='keith'):
        all_exec_ids = self.retrieve_formula_instance_executions_ids()
        for i in range(len(all_exec_ids)-1, 0, -1):
            cur_exec = self.get_formula_instance_execution(
                execution_id=all_exec_ids[i]).json()
            if self._search_trigger(cur_exec, search_str):
                yield all_exec_ids[i]

    def find_all_my_exec(self,
                         exit_after=None,
                         search_str='keith'):
        all_exec_ids = self.retrieve_formula_instance_executions_ids()
        if not isinstance(exit_after, int):
            exit_after = len(all_exec_ids)
        my_exec = []
        for i in range(len(all_exec_ids)-1, 0, -1):
            cur_exec = self.get_formula_instance_execution(
                execution_id=all_exec_ids[i]).json()
            if self._search_trigger(cur_exec, search_str):
                my_exec.append(all_exec_ids[i])
                if len(my_exec) == exit_after:
                    return my_exec
        return my_exec

    def _search_trigger(self,
                        execution,
                        search_str):
        desired_mapping = ['stepExecutions',
                           ('stepName', 'trigger'),
                           'stepExecutionValues',
                           ('key', 'trigger.body'),
                           'value']
        return search_str in self.iterate_dict(execution, desired_mapping)[0]

    def find_my_most_recent(self,
                            search_str='keith'):
        my_last = self.find_all_my_exec(exit_after=1, search_str=search_str)
        if len(my_last) > 0:
            return my_last[0]
        else:
            return None

    def set_my_most_recent(self,
                           search_str='keith'):
        exec_id = self.find_my_most_recent(search_str=search_str)
        self.url_vars['formula_instance_execution_id'] = exec_id
        self.cur_execution = self.get_formula_instance_execution(
            execution_id=exec_id)

    def get_trigger(self,
                    execution_json):
        for i in execution_json['stepExecutions']:
            if i['stepName'] == 'trigger':
                return i

    def reset_all_formulas(self):
        """
        This Function will delete all instances of all the formulas then 
        will delete all the formulas themselves.

        USE WITH CAUTION!!
        """
        all_instances = list(self.send_page_request('get', self.formula_instance_path))
        all_formulas = self.retrieve_formula_ids()
        for instances in all_instances:
            for instance in instances:
                self.delete_formula_instance(
                    formula_id=instance['formula']['id'],
                    instance_id=instance['id'])
        for formula in all_formulas:
            self.delete_formula(formula_id=formula)



