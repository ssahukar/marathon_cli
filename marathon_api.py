#   Copyright 2015 Shridhar Sahukar
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import httplib
import json
import re

class MarathonApiFailedException(Exception):
    pass


class MarathonApi(object):
    def __init__(self, ip, port):
        super(self.__class__, self).__init__()
        self.ip = ip
        self.port = port

    def _api_request(self, method, uri, body=None, headers={}, ok_code=200):
        conn = httplib.HTTPConnection(self.ip, self.port)
        req = conn.request(method, uri, body, headers)
        resp = conn.getresponse()
        if resp.status != ok_code:
            print "API Request {} for {} failed with resp code {}".format(
                    method, uri, resp.status)
            data = resp.read()
            print data
            raise MarathonApiFailedException()

        data = resp.read()
        data = json.loads(data)
        return (resp.status, data)

    def create_app(self, app_json_file_path):
        app_data = None
        with open(app_json_file_path, 'r') as f:
            data = f.read()
            try:
                app_data = json.loads(data)
            except Exception, e:
                print "Invalid json file"
                print e
                return

        if not app_data:
            print "Invalid app data. Failed to create the app"

        ret_code, data = self._api_request("POST", "/v2/apps", json.dumps(app_data), {'Content-Type': 'application/json'}, ok_code=201)
        return data

    def destroy_app(self, appids):
        for appid in appids.split():
            try:
                ret_code, data = self._api_request("DELETE", "/v2/apps/{}".format(appid))
                print data
            except:
                pass

    def get_apps(self):
        ret_code, data = self._api_request("GET", "/v2/apps")

        apps = data['apps']
        return apps

    def get_app(self, appid):
        if not appid or not len(appid):
            print "Usage: app <appid>"
            return

        #Remove starting / from the appid if any
        appid = appid.lstrip('/')

        ret_code, data = self._api_request("GET", "/v2/apps/{}".format(appid))

        app = data['app']
        return app

    def scale_app(self, appid, num_units):
        #Get the number of existing instances
        ret_code, data = self._api_request("GET", "/v2/apps/{}".format(appid.lstrip('/')))

        app = data['app']
        cur_instances = app['instances']
        total_instances_required = int(cur_instances) + int(num_units)

        if total_instances_required <= 0:
            print "ERR: Atleast one instance must be running. Cannot delete {} units from {} running units".format(
                    num_units, cur_instances)
            return None

        uri = "/v2/apps/{}?force=true".format(appid.lstrip('/'))
        req_data = {"id": appid,
                    "instances": total_instances_required}

        ret_code, data = self._api_request("PUT", uri, json.dumps(req_data))

        print "Total number of units for app {} is {}".format(appid, total_instances_required)

        return data

    def scale_app_to_units(self, appid, num_units):
        '''This function is slightly different than the scale_app.
           This takes the absolute number of units to be scaled for the given app
        '''

        uri = "/v2/apps/{}?force=true".format(appid.lstrip('/'))
        req_data = {"id": appid,
                    "instances": num_units}

        ret_code, data = self._api_request("PUT", uri, json.dumps(req_data))

        print "Total number of units for app {} is {}".format(appid, num_units)

        return data

    def restart_app(self, appid):
        if not appid or not len(appid):
            return None

        #Remove starting / from the appid if any
        appid = appid.lstrip('/')

        ret_code, data = self._api_request("POST", "/v2/apps/{}/restart".format(appid))

        return data

    def get_app_tasks(self, appid):
        if not appid or not len(appid):
            return None

        #Remove starting / from the appid if any
        appid = appid.lstrip('/')

        ret_code, data = self._api_request("GET", "/v2/apps/{}/tasks".format(appid))

        return data

    def delete_all_tasks(self, appid):
        if not appid or not len(appid):
            return None


        #Remove starting / from the appid if any
        appid = appid.lstrip('/')

        ret_code, data = self._api_request("DELETE", "/v2/apps/{}/tasks".format(appid))

        return data

    def get_all_tasks(self):
        ret_code, data = self._api_request("GET", "/v2/tasks")

        return data


    def get_event_subscribers(self):
        ret_code, data = self._api_request("GET", "/v2/eventSubscriptions")
        subscribers = data['callbackUrls']
        return subscribers

    def delete_event_subscriber(self, tobe_deleted):
        #Get the current subscribers
        ret_code, data = self._api_request("GET", "/v2/eventSubscriptions")
        subscribers = data['callbackUrls']

        if tobe_deleted not in subscribers:
            print "ERR: Subscriber {} is not in subscriber list".format(tobe_deleted)
            return

        ret_code, data = self._api_request("DELETE",
                                           "/v2/eventSubscriptions?callbackUrl={}".format(tobe_deleted))

    def add_event_subscriber(self, subscriber_url):
         ret_code, data = self._api_request("POST",
                                            "/v2/eventSubscriptions?callbackUrl={}".format(subscriber_url))

    def get_deployments(self):
        ret_code, data = self._api_request("GET", "/v2/deployments")
        return data

    def get_task_queue(self):
        ret_code, data = self._api_request("GET", "/v2/queue")
        return data

    def get_server_info(self):
        ret_code, data = self._api_request("GET", "/v2/info")
        return data
