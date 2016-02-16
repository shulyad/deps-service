# -*- coding: utf-8 -*-
import os
from menu import *
from fabric.api import *
from fabric.contrib.files import exists
from os.path import join

def mkdir_p(path):  # Создает директории на удаленной машине
    run('mkdir -p ' + path)


def mkdir_p_local(path):  # Создает директории на локальной машине
    local('mkdir -p ' + path)


def listdir(path):  # Выдает список файлов/директорий
    pathToFiles = []
    for dirname, dirnames, filenames in os.walk(path):
        for filename in filenames:
            pathToFiles.append(os.path.join(dirname, filename))
        if '.git' in dirnames:
            dirnames.remove('.git')
    return(pathToFiles)

def remEmptyDir(path): # Удаляет пустые директории
    for root, dirs, files in os.walk(path,topdown=False):
        for name in dirs:
            fname = join(root,name)
            if not os.listdir(fname): #to check wither the dir is empty
                #print fname
                os.removedirs(fname)
def f(s): # Тестовая функция дл вывода в консоль.
    print s

@task()
def test_rc():
    print(local_releases_root)

@task(name='web-do')
def upload_to_server(release):
    """#### Example: fab upload_to_server:release=20150725T115311 ####"""
    run('mkdir -p /var/local/releases')
    put('releases/%s/' % release, '/var/local/releases', mode=0775)
    run('chown -R deps:adm /var/local/releases')
    sudo(preCommand, shell=False)
    run('find ' + service_root + ' -type l | xargs -i unlink {}')
    run('find /var/local/releases/%s/ -mindepth 1 -depth -type d -printf "%%P\\n" | while read dir; do mkdir -p %s/$dir; done' % (release, service_root), shell=False)
    run('find /var/local/releases/%s/ -type f -printf "%%P\\n" | while read file; do ln -sf /var/local/releases/%s/$file %s/$file; done' % (release, release, service_root))
    sudo(postCommand, shell=False)
    with cd('/var/local/releases'):
        run('rm -fr `ls -t | tail -n +2`')

@task(name='do')
def choose_release():
    """- Example: fab do -H server-hostname-or-ip-address"""
    remEmptyDir('releases')
    sorted_release_folder = os.listdir(local_releases_root)
    sorted_release_folder.sort()
    sorted_release_folder.reverse()
    m = Menu("########## Выбирите релиз ##########")
    for release_folder in sorted_release_folder:
        if os.path.isdir(os.path.join(local_releases_root,release_folder)):
            m.addoption(release_folder, lambda a=release_folder:upload_to_server(a))
    m.start()
