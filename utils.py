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
import re
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def columnize(data, header=False, indent=0):
    num_rows = len(data)
    num_cols = len(data[0])
    _list = []
    for j in range(0, num_cols):
        new_list = []
        for i in range(0, num_rows):
            new_list.append(data[i][j])
        _list.append(new_list)

    max_lens = []
    for col in _list:
        max_len = 0
        for x in col:
            if len(str(x)) > max_len:
                max_len = len(str(x))
        max_lens.append(max_len)

    totalsize = sum(max_lens) + 2*(num_cols-1)
    if header:
        print ' '*indent,
        for j in range(0, num_cols):
            print bcolors.OKBLUE + "{}".format(data[0][j]).rjust(max_lens[j]) + bcolors.ENDC + " ",
        print ""
        print ' '*indent,
        print '-'*totalsize
            
    for i in range(1, num_rows):
        print ' '*indent,
        for j in range(0, num_cols):
            print "%s " % str(data[i][j]).rjust(max_lens[j]),
        print ""
    print ""


def print_app_data(app):
    '''Print app data
    '''
    print "AppInfo for {}".format(app['id'])
    print bcolors.OKBLUE + "  Attributes" + bcolors.ENDC
    for key in ['version', 'user','cmd', 'args', 'env', 'constraints',
                      'instances', 'cpus', 'mem', 'disk', 'ports', 'executor',
                      'dependencies', 'healthChecks', 'deployments', 'uris',
                      'upgradeStrategy']:
        if key in app:
            print " ", key.title().ljust(21), ": {}".format(app[key])

    print "  Container Type       : {}".format(app['container']['type'])

    if app['container']['type'] == 'DOCKER':
        print ""
        print bcolors.OKBLUE + "  Docker Container Details" + bcolors.ENDC
        for name, key in [("Image",'image'), ("Parameters", "parameters"),
                          ("Network", "network"), ("Port Mappings", "portMappings"),
                          ("Privileged", "privileged")]:
            if key in app['container']['docker']:
                print " ", name.ljust(21), ": {}".format(app['container']['docker'][key])

    print ""
    print bcolors.OKBLUE + "  Container Volumes" + bcolors.ENDC
    volume_info = [["ContainerPath", "HostPath", "Mode"]]    
    for vol in app['container']['volumes']:
        vol = [vol['containerPath'], vol['hostPath'], vol['mode']]
        volume_info.append(vol)

    columnize(volume_info, True, 1)


    print ""
    print bcolors.OKBLUE + "  Parameters" + bcolors.ENDC

    print "  BackoffFactor        : {}".format(app['backoffFactor'])
    print "  BackoffSeconds       : {}".format(app['backoffSeconds'])
    print "  RequirePorts         : {}".format(app['requirePorts'])

    print ""
    print bcolors.OKBLUE + "  Tasks" + bcolors.ENDC

    print "  TasksStaged          : {}".format(app['tasksStaged'])
    print "  TasksRunning         : {}".format(app['tasksRunning'])
    print "  LastTaskFailure      : {}".format(app['lastTaskFailure'])


    tasks = [["TaskId", "Host", "Ports", "StagedAt", "StartedAt", "Version"]]
    for task in app['tasks']:
        taskInfo = [task['id'], task['host'], task['ports'],
                    task['stagedAt'], task['startedAt'], task['version']]
        taskInfo = [str(i) for i in taskInfo]
        tasks.append(taskInfo)

    print ""
    print bcolors.OKBLUE + "  Tasks Details" + bcolors.ENDC

    columnize(tasks, True, 1)


def print_apps_data(apps, regex):
    r = re.compile(regex)
    app_info = [["AppId", "NumInstances", "Staged", "Running", "CPUs", "Mem"]]

    for app in apps:
        if not r.search(app['id']):
            continue
        info = [app['id'], app['instances'], app['tasksStaged'],
                app['tasksRunning'], app['cpus'], app['mem']]
        #Some elements could be integers. Convert all to strings
        info = [str(i) for i in info]
        app_info.append(info)

    columnize(app_info, True)
