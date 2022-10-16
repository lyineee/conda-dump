import json
import os
import shutil
from packaging import version
from typing import List

from dep_tree import DependInfo, DependReq, DependTree

conda_base = "C:/Users/liuzh/miniconda3/envs"


def info_parser(data: dict) -> DependInfo:
    info = DependInfo(
        name=data["name"], version=version.Version(data["version"]), files=data["files"]
    )
    if "link" in data.keys():
        info.link = data["link"]["target"].replace("\\", "/")
    return info


def dep_parser(dep_list: list) -> List[DependReq]:
    """{name: name, gt: version, lt: version}"""
    re = []
    for dep in dep_list:
        dep_req = DependReq(dep.split()[0])
        if len(dep.split()) > 1:
            for req in dep.split()[1].split(","):
                if req.startswith(">="):
                    dep_req.gt = version.Version(req[2:])
                elif req.startswith("<="):
                    dep_req.lt = version.Version(req[2:])
                elif req.startswith("<"):
                    dep_req.lt = version.Version(req[1:])
                elif req.startswith("!="):
                    dep_req.ne = version.Version(req[2:])
                else:
                    print(f"unmatch {req}")
        re.append(dep_req)
    return re


def search_dep(dep_list: List[DependReq]) -> dict:
    base = conda_base + "/envs/opencv"
    prefix = "/conda-meta"
    for dep in dep_list:
        found_flag = False
        for path in os.listdir(base + prefix):
            info = os.path.split(path)[-1].split("-")
            if len(info) < 2:
                continue
            info = ["-".join(info[:-2]), info[-2]]
            if info[0] == dep:
                if not dep.meet(version.Version(info[1])):
                    print(
                        f"found depend {info}, but do not match req {dep}, continue searching"
                    )
            if info[0] == dep["name"] and test_version(info[1], dep):
                found_flag = True
                yield "conda-meta/" + path
                break

        if not found_flag:
            print(f'warning: deppend {dep["name"]} no found')


def purne(dep_list: List[DependReq]) -> List[DependReq]:
    ex_list = ["python", "vc", "vs2015_runtime"]
    re = []
    for dep in dep_list:
        flag = False
        for ex in ex_list:
            if ex == dep:
                flag = True
        if not flag:
            re.append(dep)
    return re


def dep(path) -> DependTree:
    conda_path = conda_base + "/envs/opencv"
    in_json = {}
    with open(conda_path + "/" + path, "r") as f:
        in_json = json.load(f)
    dep_list = dep_parser(in_json["depends"])
    dep_list = purne(dep_list)
    node = DependTree(info_parser(in_json))
    if not dep_list:
        return node
    re.update([path])
    for i in search_dep(dep_list):
        node.append(*dep(i))
    return re


def get_lib(f_list):
    conda_path = conda_base + "/envs/opencv"
    lib_list = set()
    for f_path in f_list:
        with open(conda_path + "/" + f_path, "r") as f:
            j = json.load(f)
            lib_list.update(j["files"])
    return lib_list


def copy_all(lib_list, base="./Documents/note-book"):
    conda_path = conda_base + "/envs/opencv"
    err_count = 0
    copy_count = 0
    for file_path in lib_list:
        dir = os.path.dirname(file_path)
        src = conda_path + "/" + file_path
        dst_dir = base + "/" + dir
        dst = base + "/" + file_path
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        if not os.path.exists(src):
            print(f'file not found "{src}"')
            err_count += 1
            continue
        if not os.path.exists(dst):
            shutil.copy(src, dst)
            copy_count += 1
            print(f'copying "{src}" to "{dst}"', end="\r")
