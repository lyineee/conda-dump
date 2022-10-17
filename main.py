import json
import os
import shutil
from packaging import version
from typing import Optional

from dep_tree import DependInfo, DependReq, DependTree

conda_base = "C:/Users/liuzh/miniconda3/envs"


def dep_info_parser(data: dict) -> DependInfo:
    info = DependInfo(
        name=data["name"], version=version.parse(data["version"]), files=data["files"]
    )
    if data["link"]["source"] != "":
        info.link = data["link"]["source"].replace("\\", "/")

    # parse depend requirements
    for req_str in data["depends"]:
        info.depends.append(dep_req_parser(req_str))

    return info


def dep_req_parser(dep_str: str) -> DependReq:
    dep_req = DependReq(dep_str.split()[0])
    if len(dep_str.split()) > 1:
        for req in dep_str.split()[1].split(","):
            if req.startswith(">="):
                dep_req.gt = version.parse(req[2:])
            elif req.startswith("<="):
                dep_req.lt = version.parse(req[2:])
            elif req.startswith("<"):
                dep_req.lt = version.parse(req[1:])
            elif req.startswith("!="):
                dep_req.ne = version.parse(req[2:])
            elif req[0].isdigit():
                dep_req.eq = version.parse(req)
            else:
                print(f"unmatch {req} in depend requirement {dep_req.name}")
    return dep_req


def search_dep(dep_req: DependReq) -> DependInfo:
    base = conda_base + "/envs/notebook"
    prefix = "/conda-meta"
    for path in os.listdir(base + prefix):
        info = os.path.split(path)[-1].split("-")
        if len(info) < 2:
            continue
        info = ["-".join(info[:-2]), info[-2]]
        if info[0] == dep_req.name:
            if not dep_req.meet_version(version.parse(info[1])):
                print(
                    f"found depend {info}, but do not match req {dep}, continue searching"
                )
            else:
                with open(base + "/conda-meta/" + path, "r") as f:
                    data = json.load(f)
                    return dep_info_parser(data)
    raise RuntimeWarning(f'deppend {dep} no found')


def dep(dep_info: DependInfo) -> DependTree:
    node = DependTree(dep_info)
    if len(dep_info.depends) == 0:
        return node
    for dep_req in dep_info.depends:
        info = search_dep(dep_req)
        if info.name in ["vs2015_runtime", "vc", "python"] or info in node:
            continue
        node.append(dep(info))
    return node


def get_lib(dep_tree: DependTree) -> set:
    file_set = set()
    for dep_info in dep_tree:
        file_set.update(dep_info.files)
    return file_set


def copy_all(lib_list, base="./Documents/note-book"):
    conda_path = conda_base + "/envs/notebook"
    err_count = 0
    copy_count = 0
    all_count = len(lib_list)
    progress_count = 0
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

        # progress bar
        file_name = os.path.split(file_path)[-1]
        width = 20
        progress_count += 1
        c = int((progress_count / all_count) * width) + 1
        bar = "|" + (c * "-").ljust(width) + "|"
        print(f'{bar}{progress_count}/{all_count} processing "{file_name}"', end="")
        print(f'{" "*100}', end="\r")  # clean line
        # print(f'{copy_count}/{all_count}  copying "{src}" to "{dst}"', end="\r")
    print("")
    print(
        f"finish copy, total: {len(lib_list)}, copy: {copy_count}, error: {err_count}"
    )


if __name__ == "__main__":
    req = DependReq(name="notebook")
    dep_info = search_dep(req)
    a = dep(dep_info)
