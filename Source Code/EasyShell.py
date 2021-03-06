# -*- coding:utf-8 -*-
from EasyScript import *
import sys
import yaml
import os
import argparse
import platform
import datetime
import getpass


def GetSystemDevices():
    import psutil
    for x in psutil.disk_partitions():
        try:
            os.access(f"{x[1]}Windows", os.F_OK)
        except FileNotFoundError:
            pass
        else:
            SystemDevice = x[1]
            break
    return SystemDevice


# 设置AppData存放位置
if os.name == 'nt':
    if os.getenv('APPDATA'):
        AppDataDir = f"{os.getenv('APPDATA')}/Local/"
        if os.access(f"{AppDataDir}EasyPython", os.F_OK):
            AppDataDir = f"{os.getenv('APPDATA')}/Local/EasyPython"
        else:
            os.mkdir(f"{AppDataDir}EasyPython")
            AppDataDir = f"{os.getenv('APPDATA')}/Local/EasyPython"
    else:
        AppDataDir = f"{GetSystemDevices()}User/{getpass.getuser()}/AppData/Local/"
        if os.access(f"{AppDataDir}EasyPython", os.F_OK):
            AppDataDir = f"{os.getenv('APPDATA')}/Local/EasyPython"
        else:
            os.mkdir(f"{AppDataDir}EasyPython")
            AppDataDir = f"{os.getenv('APPDATA')}/Local/EasyPython"

else:
    if os.getenv('HOME'):
        AppDataDir = f"{os.getenv('HOME')}/.config/"
        if os.access(f"{AppDataDir}EasyPython", os.F_OK):
            AppDataDir = f"{os.getenv('HOME')}/.config/EasyPython"
        else:
            os.mkdir(f"{AppDataDir}EasyPython")
            AppDataDir = f"{os.getenv('HOME')}/.config/EasyPython"
    else:
        AppDataDir = f"/home/{getpass.getuser()}/.config/"
        if os.access(f"{AppDataDir}EasyPython", os.F_OK):
            AppDataDir = f"{os.getenv('HOME')}/.config/EasyPython"
        else:
            os.mkdir(f"{AppDataDir}EasyPython")
            AppDataDir = f"{os.getenv('HOME')}/.config/EasyPython"

# 读取 config.yml 文件
# with open("EasyScript/config.yml") as f:
# config = yaml.safe_load(f.read())
try:
    with open(f"{AppDataDir}/config.yml") as f:
        config = yaml.safe_load(f.read())
except FileNotFoundError or PermissionError:
    print("Config File Not Found, Creating.")
    with open("EasyScript/config.yml") as t:
        with open(f"{AppDataDir}/config.yml", 'w') as f:
            f.write(t.read())
    config = yaml.safe_load(open(f"{AppDataDir}/config.yml").read())

if config['options']['fix-move-keys'] and os.name != 'nt':
    import readline

# 初始化argparse
# prog: Usage中的程序名
# description: -h 中的程序介绍
ArgParser = argparse.ArgumentParser(prog="EasyPython",
                                    description="""\
    an easy to learn and easy to use programming language developed in Python.
    """)

# 初始化非共存组
NonCoexistentGroup = ArgParser.add_mutually_exclusive_group()

# 添加选项 -i
# action: 动作
# help: -h 选项下显示的内容
NonCoexistentGroup.add_argument("-i",
                                "--interactive",
                                action="store_true",
                                help="Use interactive mode. [Default Option]")

# 添加选项 -f
# type: 自动转化类型
# help: -h 选项下显示的内容
NonCoexistentGroup.add_argument("-f",
                                "--file",
                                type=str,
                                help="Run the easypython code file.")

# 添加选项
# action: 动作
# help: -h 选项下显示的内容
ArgParser.add_argument("-v",
                       "--version",
                       action="store_true",
                       help="Get the version of the EasyPython.")

# 添加选项
ArgParser.add_argument("--fix-move-keys",
                       action="store_true",
                       help="Fix the problem of moving keys. [Only For Linux]")

# 分析参数
args = ArgParser.parse_args()
# print(args)

# 如果无任何参数
if args.interactive is False and args.version is False and not args.file:
    # 互交模式启动
    args.interactive = True
else:
    # 否则不进行任何操作
    pass
# 主版本号
MAJAR_VERSION = config['options']['majar-version']

# 副版本号
MINOR_VERSION = config['options']['minor-version']
# 补丁号
PATCH_VERSION = config['options']['patch-version']


def get_release_time():
    with open("EasyScript/config.yml") as f:
        config = yaml.safe_load(f.read())
    release_months_dict = {
        '1': "Jan",
        '2': "Feb",
        '3': "Mar",
        '4': "Apr",
        '5': "May",
        '6': "Jun",
        '7': "Jul",
        '8': "Aug",
        '9': "Sept",
        '10': "Oct",
        '11': "Nov",
        '12': "Dec"
    }  # 创建月份字典

    # 发布日期↓
    release_date_time = f"""\
{str(config["release-datetime"]['release_year'])} {release_months_dict[str(config["release-datetime"]['release_month'])]} {str(config["release-datetime"]['release_day'])}, {str(config['release-datetime']['release_hour'])}:{str(config['release-datetime']['release_min'])}:{str(config['release-datetime']['release_sec'])}"""
    return release_date_time


def shell(name="<stdin>", RunFile=False, command=""):
    version = f"{str(MAJAR_VERSION)}.{str(MINOR_VERSION)}.{str(PATCH_VERSION)}"
    release_date_time = get_release_time()
    # 启动时显示的帮助信息
    start_help_info = '"help", "copyright"'
    # 输出启动信息
    if not RunFile:
        print(
            f"EasyPy(EasyPython) v{version}, (Released in {release_date_time}). \nRun EasyPy on {sys.platform}, {platform.platform()}.\nType {start_help_info} for more information.\nSource Code:https://gitee.com/ky-studio/EasyPython"
        )
    # 循环
    while True:
        # 获取用户输入信息
        if not RunFile:
            command = input('EasyPy >>> ')

        # 如果用户输入了exit
        if command == 'exit':
            # 退出并打印信息
            print("If you want to exit, please use '.exit'.")

        elif command == '.exit':
            sys.exit("Good bye, Thanks for using.")

        elif command.strip() == "":
            continue

        elif command == 'copyright':
            author = "yps and __init__"
            if datetime.datetime.now().year == 2021:
                year = "2021"
            else:
                year = '2021 - ' + str(datetime.datetime.now().year)
            print("Copyleft © {year} , {author}. Some rights reserved".format(
                year=year, author=author))  # 版权信息提示

        else:
            # 获取返回值与错误
            result, error = run(name, command)

            # 如果错误有具体内容
            if error:
                # 调用error的as_string方法
                print(error.as_string())
            # 如果有返回值
            elif result:
                # 打印返回值
                if len(result.elements) == 1:
                    print(repr(result.elements[0]))
                else:
                    print(repr(result))

        if RunFile:
            break


if __name__ == '__main__':
    if config["options"]["fix-move-keys"] is False:
        print(
            "Tips: If you have problems with your move keys, please add the '--fix-move-keys' option"
        )
    else:
        pass
    # 如果给有 -f 参数
    if args.file:
        # 如果可以读取文件
        if os.access(args.file, os.R_OK):
            path, temp = os.path.split(args.file)
            file_name, extension = os.path.splitext(temp)
            with open(args.file) as f:
                shell(f"{file_name}{extension}", True, f.read())
        else:
            raise PermissionError(f"Cannot open file {args.file}.")
    # 如果带有 --fix-move-keys
    if args.fix_move_keys is True:
        if os.name != 'nt':
            if not config['options']['fix-move-keys']:
                user_input = input(
                    'It is detected that you have added the --fix-move-keys option. Do you need to fix the problem permanently? [Y/n]:'
                )
                if user_input == 'y' or user_input == 'Y' or user_input == '':
                    with open("EasyScript/config.yml", 'w') as f:
                        config['options']['fix-move-keys'] = True
                        f.write(yaml.dump(config))
                    import readline
                else:
                    import readline
        else:
            pass
    # 如果有给 -i 或任何参数也没有
    if args.interactive:
        # 进入shell
        shell()
    # 如果有 -v 参数
    if args.version:
        # 打印版本号
        print(
            f"EasyPython {str(MAJAR_VERSION)}.{str(MINOR_VERSION)}.{str(PATCH_VERSION)}"
        )
