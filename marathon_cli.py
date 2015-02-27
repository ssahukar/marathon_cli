#!/usr/bin/python

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

#Import cmd2 if available, else import cmd
try:
    from cmd2 import Cmd
except ImportError:
    print "WARN: cmd2 module is not available. Using cmd module with limited features"
    print "      Install python-cmd2 package to resolve this issue"
    from cmd import Cmd

import argparse
import subprocess
import os
import sys
import json
import pprint

from utils import columnize, print_app_data, print_apps_data
from marathon_api import MarathonApi


class MarathonCli(Cmd, object):
    """Simple command processor example."""
    def __init__(self, ip=None, port=None):
        super(self.__class__, self).__init__()
        self.ip = ip
        self.port = port
        if ip and port:
            self.connect("{} {}".format(self.ip, self.port))

    def connect(self, line):
        ip, port = line.split()
        self.marathon_api = MarathonApi(ip, port)

    def emptyline(line):
        pass

    def do_apps(self, regex):
        '''Print list of apps
           Usage: apps [filter]

           The optional 'filter' is used to list only those apps that match
           the regex for the given filter
        '''
        apps = self.marathon_api.get_apps()
        print_apps_data(apps, regex)

    def do_app(self, appid):
        '''Print details of a given app
           Usage: app <appid>
        '''
        if appid == None or len(appid) == 0:
            print "ERR: Appid must be provided"
            print "USAGE: app <appid>"
            return

        try:
            app = self.marathon_api.get_app(appid)
        except Exception, e:
            print "ERR: Failed to fetch app details - {}".format(e)
            return

        print_app_data(app)

    def do_create_app(self, app_json_file_path):
        '''Create an app 
           Usage: create_app <app_json_file_path>
        '''
        if not os.path.isfile(app_json_file_path):
            print "ERR: app_json_file_path is invalid. Specify a proper json file"
            return
        self.marathon_api.create_app(app_json_file_path)


    def do_destroy_app(self, appids):
        '''Destroy the app with appid
           Usage: destroy_app <appid>
        '''
        if appids == None or len(appids) == 0:
            print "ERR: Appid must be provided"
            print "USAGE: app <appid>"
            return

        self.marathon_api.destroy_app(appids)

    def do_scale_app(self, args):
        '''Scale an app.
           Usage: scale_app <appid> <num_units>
                  
                  num_units : if +ve value, given number of units will be added
                              if -ve value, given number of units will be removed
        '''
        try:
            appid, num_units = args.split()
        except:
            print "Usage: add_units <appid> <num_units>"
            print "      num_units : if +ve value, given number of units will be added"
            print "                  if -ve value, given number of units will be removed"
            return

        data = self.marathon_api.scale_app(appid, num_units)
        if not data:
            return
        print "   DeploymentID : {}".format(data['deploymentId'])
        print "   Version      : {}".format(data['version'])

    def do_restart_app(self, appid):
        '''Restart all tasks of an app
           Usage: restart_app <appid>
        '''
        if appid == None or len(appid) == 0:
            print "ERR: Appid must be provided"
            print "USAGE: app <appid>"
            return

        data = self.marathon_api.restart_app(appid)
        if not data:
            return
        print "   DeploymentID : {}".format(data['deploymentId'])
        print "   Version      : {}".format(data['version'])

    def do_app_tasks(self, appid):
        '''List all tasks of given appid
           Usage: tasks <appid>
        '''
        if appid == None or len(appid) == 0:
            print "ERR: Appid must be provided"
            print "USAGE: app <appid>"
            return

        data = self.marathon_api.get_app_tasks(appid)
        if not len(data['tasks']):
            print "No tasks found for app {}".format(appid)
            return

        columns = [data['tasks'][0].keys()]
        for task in data['tasks']:
            columns.append(task.values())
        columnize(columns, True, 1)

    def do_delete_all_tasks(self, appid):
        '''Delete all tasks of an appid
           Usage: delete_all_tasks <appid>
        '''
        if appid == None or len(appid) == 0:
            print "ERR: Appid must be provided"
            print "USAGE: app <appid>"
            return

        print "This command will delete all the tasks in this app"
        while True:
            val = raw_input("Are you sure you want to continue y/N: ")
            if val.lower() in ['y', 'n']:
                break
        if val.lower() == 'n':
            return

        data = self.marathon_api.delete_all_tasks(appid)
        columns = [data['tasks'][0].keys()]
        for task in data['tasks']:
            columns.append(task.values())
        columnize(columns, True, 1)

    def do_all_tasks(self, line):
        '''Print all tasks in the system
           Usage: all_tasks
        '''
        data = self.marathon_api.get_all_tasks()
        columns = [data['tasks'][0].keys()]
        for task in data['tasks']:
            columns.append(task.values())
        columnize(columns, True, 1)

    def do_list_event_subscribers(self, line):
        '''Print the list of event subscribers
           Usage: list_event_subscribers
        '''
        subscribers = self.marathon_api.get_event_subscribers()
        columns = [["SubscriberURIs"]]
        for sub in subscribers:
            columns.append([sub])
        columnize(columns, True, 1)

    def do_delete_event_subscriber(self, tobe_deleted):
        '''Delete a given event subscriber
           Usage: delete_event_subscriber <subscriber>
        '''
        if not tobe_deleted:
            print "ERR: The subscriber to be deleted must be specified"
            print "Usage: delete_event_subscriber <subscriber>"
            return

        self.marathon_api.delete_event_subscriber(tobe_deleted)
        print "Event subscriber has been deleted"
        

    def do_deployments(self, line):
        '''Print list of pending deployments
           Usage: deployments
        '''
        data = self.marathon_api.get_deployments()
        pprint.pprint(data)

    def do_task_queue(self, line):
        '''Print the task queue
           Usage: task_queue
        '''
        data = self.marathon_api.get_task_queue()
        columns = [["ID", "Instances", "TasksQueued"]]
        for app in data['queue']:
            columns.append([app['app']['id'], app['app']['instances'], app['count']])
        columnize(columns, True, 1)

    def do_server_info(self, line):
        '''Print the server information
           Usage: server_info
        '''

        data = self.marathon_api.get_server_info()
        pprint.pprint(data)

    def do_shell(self, cmd):
        '''Run any shell command from this prompt
           Usage: shell <shell_command>
                    or
                  ! <shell_command>
        '''
        try:
            out = subprocess.check_output(cmd, shell=True)
            print out
        except subprocess.CalledProcessError, e:
            print e

    def do_quit(self, line):
        sys.exit(0)

    def do_exit(self, line):
        sys.exit(0)

    def do_EOF(self, line):
        sys.exit(0)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", type=str, help="IP address of marathon master")
    parser.add_argument("port", type=int, help="Port of marathon master")
    args = parser.parse_args()
    cli = MarathonCli(args.ip, args.port)
    while True:
        try:
            cli.cmdloop()
        except KeyboardInterrupt:
            print ""
            continue
