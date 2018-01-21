import threading
import time
import yaml
import argparse

deps = {}
deps_2 = {}
hosts = {}
layered = []
app_list = []
no_deps = []
full_list = []

parser = argparse.ArgumentParser("WHAT???")
parser.add_argument('action', type=str, help='start/stop')
parser.add_argument("apps", type=str, help='apps to stop/start')
values = parser.parse_args()
to_start = str.split(values.apps, ",")
action = values.action

pb = yaml.safe_load(open('Boom.yaml'))


def parse_yaml():
    for pbitems in pb.items():
        temp = str
        for apps in pbitems:
            if type(apps) is str:
                app_list.append(apps)
                temp = apps
            else:
                if apps.get("deps"):
                    for depss in apps.get("deps"):
                        deps[temp] = apps.get("deps")
                for host in apps.get("hosts"):
                    hosts[temp] = apps.get("hosts")


def no_deps_apps():
    for app in app_list:
        if app not in deps.keys():
            no_deps.append(app)


def sort():
    apps_with_dependencies = len(app_list) - len(no_deps)
    switch = True
    iterations = 0
    to_append = []
    deps_for_sort = deps.copy()
    while switch:
        if len(to_append) == 0:
            deps_for_sort_2 = deps_for_sort.copy()
            for application_name, list_of_app_dependecies in deps_for_sort_2.items():
                layered_copy = layered.copy()
                dependencies_match = []
                length_of_list_of_all_dependencies = len(list_of_app_dependecies)
                for dependencies_of_app in list_of_app_dependecies:
                    for group_of_layered_apps in layered_copy:
                        for layered_app_name in group_of_layered_apps:
                            if dependencies_of_app == layered_app_name:
                                dependencies_match.append(dependencies_of_app)
                                if len(dependencies_match) == length_of_list_of_all_dependencies:
                                    to_append.append(application_name)
                                    iterations = iterations + 1
                                    del deps_for_sort[application_name]

        else:
            layered.append(to_append.copy())
            del to_append[:]
            if apps_with_dependencies == iterations:
                switch = False


def deps_2_create():
    temp_list = []
    counter = 0
    entered = []
    for layers in layered:
        for applications in to_start:
            if applications in layers:
                entered.append(applications)

    for app_to_start in entered:
        full_list.append(app_to_start)
        for application_name, list_of_app_dependencies in deps.items():
            for dep in list_of_app_dependencies:
                if action == "start":
                    if application_name == app_to_start:
                        full_list.append(dep)
                        temp_list.append(dep)
                if action == "stop":
                    if dep == app_to_start:
                        full_list.append(application_name)
                        temp_list.append(application_name)
    trigger = True
    while trigger:
        temp_list_2 = temp_list.copy()
        del temp_list[:]
        for dependency in temp_list_2:
            for application_name, list_of_app_dependencies in deps.items():
                if action == "start":
                    if dependency == application_name:
                        for dep in list_of_app_dependencies:
                            full_list.append(dep)
                            temp_list.append(dep)
                if action == "stop":
                    if dependency in list_of_app_dependencies:
                        full_list.append(application_name)
                        temp_list.append(application_name)

        counter = counter + 1
        if counter == len(layered):
            trigger == False
            break


def work_with_app(action, app_to_work_with):
    if action == "start":
        print("starting", app_to_work_with, "on", hosts[app_to_work_with])
    else:
        print("stopping", app_to_work_with, "on", hosts[app_to_work_with])


if __name__ == '__main__':

    parse_yaml()
    no_deps_apps()
    layered.append(no_deps)
    sort()
    deps_2_create()
    done = []
    if action == "start":
        for layers in layered:
            for app_to_start in full_list:
                if (app_to_start in layers) & (app_to_start not in done):
                    done.append(app_to_start)
                    t = threading.Thread(target=work_with_app(action, app_to_start))
                    t.start()
            time.sleep(3)
    if action == "stop":
        for layers in list(reversed(layered)):
            for app_to_start in full_list:
                if (app_to_start in layers) & (app_to_start not in done):
                    done.append(app_to_start)
                    t = threading.Thread(target=work_with_app(action, app_to_start))
                    t.start()
            time.sleep(3)
