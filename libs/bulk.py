from requests_wrapper import SolutionsRequests


class BulkEndpoints(SolutionsRequests):
    url_bulk = "/hubs/crm/bulk"
    url_bulk_query = url_bulk + "/query"
    url_bulk_status = url_bulk + "/{bulk_id}/status"
    url_bulk_id_object = url_bulk + "/{bulk_id}/{object_name}"
    url_bulk_errors = url_bulk + "/{bulk_id}/errors"
    url_bulk_object = url_bulk + "/{object_name}"

    def __init__(self,
                 base_url="https://qa.cloud-elements.com/elements/api-v2",
                 org_secret="6316f6eb50a96c974638245183d941fb",
                 user_secret="m0QrLSgcTJoqatNHKiFSwhQlPu5MJD2iS7rCWXRBdIY="):
        self.url = base_url
        self.org_secret = org_secret
        self.user_secret = user_secret
        super(BulkEndpoints, self).__init__()

    def start_bulk_download(self,
                            query,
                            callback_url=None,
                            last_run_date=None,
                            from_date=None,
                            to_date=None,
                            continue_from_job_id=None,
                            file_format=None):
        params = {}
        params['q'] = str(query)
        if last_run_date:
            params['lastRunDate'] = last_run_date
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if continue_from_job_id:
            params['continueFromJobId'] = continue_from_job_id
        if file_format:
            params['fileFormat'] = file_format
        headers = {'Content-Type': "text/plain;charset=UTF-8"}
        if callback_url:
            headers['Elements-Async-Callback-Url'] = callback_url
        response = self.send_request(
            'post',
            self.url_bulk_query,
            params=params,
            headers=headers)
        self.check_response(response)
        return BulkID(response.json()['id'], self)

    def start_bulk_upload(self,
                          object,
                          data_file,
                          callback_url=None,
                          identifier_field_name=None):
        params = {}
        if identifier_field_name:
            params['identifierFieldName'] = identifier_field_name
        headers = {}
        if callback_url:
            headers['Elements-Async-Callback-Url'] = callback_url
        response = self.send_request(
            'post',
            self.url_bulk_query,
            params=params,
            headers=headers,
            data=data_file)
        self.check_response(response)
        return BulkID(response.json()['id'], self)


class BulkID(object):
    def __init__(self, bulk_id, owner, callback_session=None):
        self.bulk_id = bulk_id
        self.owner = owner

    @property
    def status(self):
        url = self.owner.url_bulk_status.format(bulk_id=self.bulk_id)
        return self.owner.send_request('get', url).json()['status']

    @property
    def records_count(self):
        url = self.owner.url_bulk_status.format(bulk_id=self.bulk_id)
        return self.owner.send_request('get', url).json()['recordsCount']

    @property
    def failed_count(self):
        url = self.owner.url_bulk_status.format(bulk_id=self.bulk_id)
        return self.owner.send_request('get', url).json()['recordsFailedCount']

    def errors(self):
        url = self.owner.url_bulk_errors.format(bulk_id=self.bulk_id)
        errors = self.owner.send_request('get', url).json()
        for error in errors:
            yield error

    def download(self, object_name):
        url = self.owner.url_bulk_id_object.format(
            bulk_id=self.bulk_id,
            object_name=object_name)
        response = self.owner.send_request('get', url)
        return response


class DynamicsBulk(BulkEndpoints):
    def __init__(self, element_token="W4sjUTKsfCxOJI9kTvYydxwYaYr22nEtRHeaRVX9fyo="):
        self.token = element_token
        super(DynamicsBulk, self).__init__()

