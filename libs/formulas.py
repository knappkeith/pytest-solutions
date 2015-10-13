from requests_wrapper import FormulaEndpoints
import json


class PassTimeFormulas(FormulaEndpoints):
    def __init__(self,
                 formula_name="Dynamics CRM to QuickBooks SalesOrder",
                 instance_name="ordersTest-Keith",
                 **kwargs):
        self.formula_name = formula_name
        self.instance_name = instance_name
        super(PassTimeFormulas, self).__init__(**kwargs)

    def start(self):
        response = self.send_request('get', self.formula_path).json()
        self.url_vars['formula_id'] = self.iterate_dict(
            response,
            [('name', self.formula_name)])[0]['id']
        response = self.send_request(
            'get',
            self.formula_id_instances_path.format(**self.url_vars)).json()
        self.url_vars['formula_instance_id'] = self.iterate_dict(
            response,
            [('name', self.instance_name)])[0]['id']
        self.set_execution_id()
        self.set_all_current()

    def _find_trigger_index(self,
                            execution_json,
                            search_str):
        trigger = self.get_trigger(execution_json)
        for i in trigger['stepExecutionValues']:
            if i['key'] == 'trigger.body':
                orders = json.loads(i['value'])['message']['raw']['salesorder']
                for order_num in range(0, len(orders)):
                    if search_str in json.dumps(orders[order_num]):
                        return order_num, orders[order_num]

    def _get_my_execution_steps(self,
                                execution_json,
                                trigger_index):
        loop_start_step_name = 'salesorderLoop'
        loop_start_key = "%s.index" % loop_start_step_name
        steps = execution_json['stepExecutions']
        my_steps = []
        this_is_a_step_of_mine = False
        for step in steps:
            if step['stepName'] == loop_start_step_name:
                for value in step['stepExecutionValues']:
                    if value['key'] == loop_start_key:
                        if int(value['value']) == int(trigger_index):
                            this_is_a_step_of_mine = True
                        else:
                            this_is_a_step_of_mine = False
            if this_is_a_step_of_mine:
                my_steps.append(step)
        return my_steps

    def did_formula_succeed(self,
                             execution_json,
                             search_str='keith'):
        must_pass_step_names = ['createQuickbooksOrder']
        format_execution_steps = self.get_my_successful_execution(
            execution_json=execution_json,
            search_str=search_str)
        for i in format_execution_steps:
            if i['stepName'] in must_pass_step_names:
                must_pass_step_names.remove(i['stepName'])
        if len(must_pass_step_names) == 0:
            self.cur_execution_steps = format_execution_steps
        return len(must_pass_step_names) == 0

    def find_most_recent_success(self,
                                 search_str='keith'):
        cur_exec_gen = self.my_exec(search_str=search_str)
        while True:
            try:
                cur_exec = cur_exec_gen.next()
            except StopIteration:
                print "No More Executions with %s!" % search_str
                return None
            print "checking....%s" % cur_exec
            cur_json = self.get_formula_instance_execution(
                execution_id=cur_exec).json()
            if self.did_formula_succeed(
                    execution_json=cur_json,
                    search_str=search_str):
                return cur_exec

    def get_my_successful_execution(self,
                                    execution_json,
                                    search_str='keith'):
        trigger_index, trigger_data = self._find_trigger_index(
            execution_json=execution_json,
            search_str=search_str)
        execution_steps = self._get_my_execution_steps(
            execution_json=execution_json,
            trigger_index=trigger_index)
        format_execution_steps = self._convert_values(execution_steps)
        return format_execution_steps

    def get_qb_ref_number(self,
                          execution_json,
                          search_str='keith'):
        step = self.get_my_successful_execution(
            execution_json=execution_json,
            search_str=search_str)
        return self.iterate_dict(
            step,
            [('stepName', 'createQuickbooksOrder'),
             'stepExecutionValues',
             ('key', 'createQuickbooksOrder.request.body'),
             'value',
             'RefNumber'])[0]
