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
print(pb)


def parse_yaml():
    for pbitems in pb.items():
        temp = str
        for apps in pbitems:
            if type(apps) is str:
                app_list.append(apps)
                temp = apps
            else:
                if apps.get("deps"):
                    for dependency in apps.get("deps"):
                        deps[temp] = apps.get("deps")
                for host in apps.get("hosts"):
                    hosts[temp] = apps.get("hosts")


def no_deps_apps():
    for app in app_list:
        if app not in deps.keys():
            no_deps.append(app)
    print(no_deps)


def sort():
    #Определяем кол-во приложений с зависимостями для выхода из цикла, как только кол-во приложенийв этажах будет = кол-ву приложений с зависимостями
    apps_with_dependencies = len(app_list) - len(no_deps)
    switch = True
    iterations = 0
    #временный массив, который мы добавляем как "этаж"
    to_append = []
    #массив который мы чистим от приложений, который мы уже "проэтажировали"
    deps_for_sort = deps.copy()
    while switch:
        #в else мы его очищаем(там же у нас условие выхлода из цикла)
        if len(to_append) == 0:
            deps_for_sort_2 = deps_for_sort.copy()
            #запрашиваем пары ключ:значение
            for application_name, list_of_app_dependecies in deps_for_sort_2.items():
                layered_copy = layered.copy()
                #совпавшие зависимости для приложения
                dependencies_match = []
                #кол-во зависимостей для приложения
                length_of_list_of_all_dependencies = len(list_of_app_dependecies)
                #проходимся по каждому приложению в зависимостях
                for dependencies_of_app in list_of_app_dependecies:
                    #заглядываем на каждый этаж
                    for group_of_layered_apps in layered_copy:
                        #проходимся по приложениям на каждом этаже
                        for layered_app_name in group_of_layered_apps:
                            #сравниваем приложение в зависимостях и на этаже
                            if dependencies_of_app == layered_app_name:
                                #добавляем его в список совпавших зависимостей
                                dependencies_match.append(dependencies_of_app)
                                #сравниваем длинну зависимостей приложения и списка совпавших приложений
                                if len(dependencies_match) == length_of_list_of_all_dependencies:
                                    #добавляем его на следующий этаж
                                    to_append.append(application_name)
                                    iterations = iterations + 1
                                    #удаляем приложение из списка
                                    del deps_for_sort[application_name]

        else:
            #добавляем этаж
            layered.append(to_append.copy())
            #удаляем временный этаж
            del to_append[:]
            #как только кол-во приложений с зависимостями = кол-ву приложений добавленных на этажи выходим из цикла
            if apps_with_dependencies == iterations:
                switch = False


def deps_2_create():
    #временный список по той же самой концепции этажей
    temp_list = []
    counter = 0
    #спиок введённых приложений
    entered = []
    #эмммм, ладно
    for layers in layered:
        for applications in to_start:
            if applications in layers:
                entered.append(applications)
    #для каждого введённого приложения...
    for app_to_start in entered:
        #..добавляем его в полный список для старта/запуска..
        full_list.append(app_to_start)
        for application_name, list_of_app_dependencies in deps.items():
            #..смотрим в каждое приложение в deps для определения того, какие у него зависимости
            for dep in list_of_app_dependencies:
                if action == "start":
                    if application_name == app_to_start:
                        # если старт - мы добавляем зависимости приложения в общий и временный список
                        full_list.append(dep)
                        temp_list.append(dep)
                if action == "stop":
                    #если стоп - мы добавляем имя приложения в общий и временный список
                    if dep == app_to_start:
                        full_list.append(application_name)
                        temp_list.append(application_name)
    trigger = True
    while trigger:
        temp_list_2 = temp_list.copy()
        del temp_list[:]
        #временный список выступает для формирования последовательного списка для запуска/остановки
        for dependency in temp_list_2:
            for application_name, list_of_app_dependencies in deps.items():
                if action == "start":
                    #находим приложение, от которого зависимости
                    if dependency == application_name:
                        for dep in list_of_app_dependencies:
                            #добавляем зависимости
                            full_list.append(dep)
                            temp_list.append(dep)
                if action == "stop":
                    if dependency in list_of_app_dependencies:
                        #добавляем приложение, которое в зависимостях
                        full_list.append(application_name)
                        temp_list.append(application_name)
    #если коротко - поняв принцип действия старт или стоп, ты поймёшь что другое работает абсолютно противоположным образом
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
    print("======")
    print(deps)
    print(hosts)
    print("======")

    no_deps_apps()
    layered.append(no_deps)
    sort()
    deps_2_create()
    done = []
    # так как в full_list может быть overДОХУЯ повторов, мы смотрим какие приложения из full_list есть на последнем(в данном случае первом) этаже и если они уже не были запущены/остановлены мы запускаем/останавливаем их
    if action == "start":
        for layers in layered:
            for app_to_start in full_list:
                if (app_to_start in layers) & (app_to_start not in done):
                    done.append(app_to_start)
                    t = threading.Thread(target=work_with_app(action, app_to_start))
                    t.start()
            time.sleep(3)
    if action == "stop":
        #переворачиваем список, для того чтобы он останавливал с конца
        for layers in list(reversed(layered)):
            for app_to_start in full_list:
                if (app_to_start in layers) & (app_to_start not in done):
                    done.append(app_to_start)
                    t = threading.Thread(target=work_with_app(action, app_to_start))
                    t.start()
            time.sleep(3)
