import json
import os, sys
import shutil
from packaging import version
from typing import List
from traceback import print_exc

from .dep_tree import DependInfo, DependReq, DependTree
from .ziputil import compress_files, decompress_files

conda_base = "~/Miniconda3"
env_name = ""
print_tree = False
dry_run = False
dump_path = "~/Documents/dump"


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
                # dep_req.eq = version.parse(req)
                pass
            else:
                print(f"unmatch {dep_str} in depend requirement {dep_req.name}")
    return dep_req


def search_dep(dep_req: DependReq) -> DependInfo:
    base = conda_base + env_name
    prefix = "/conda-meta"
    for path in os.listdir(base + prefix):
        info = os.path.split(path)[-1].split("-")
        if len(info) < 2:
            continue
        info = ["-".join(info[:-2]), info[-2]]
        if info[0] == dep_req.name:
            if not dep_req.meet_version(version.parse(info[1])):
                print(
                    f"found depend {info}, but do not match req {dep_req}, continue searching"
                )
            else:
                with open(base + "/conda-meta/" + path, "r") as f:
                    try:
                        data = json.load(f)
                    except:
                        print(f"ERROR: parsing depend {dep_req}")
                        print_exc()
                        sys.exit(1)
                    return dep_info_parser(data)

    print(f"WARN: deppend {dep_req} no found")


dep_set = set()


def dep(dep_info: DependInfo, ex_list: List[DependReq] = []) -> DependTree:
    conda_path = conda_base + env_name
    node = DependTree(dep_info)
    if len(dep_info.depends) == 0:
        return node
    for dep_req in dep_info.depends:
        for exclude in ex_list:
            ex_flag = False
            if exclude.name == dep_req.name:
                ex_flag = True
        if (
            ex_flag
            or dep_req.name in ["vs2015_runtime", "vc", "python"]
            or dep_req.name in dep_set
        ):
            continue
        info = search_dep(dep_req)
        dep_set.add(info.name)
        if info in node:
            continue

        node.append(dep(info, ex_list))
    return node


def get_lib(dep_tree: DependTree) -> set:
    file_set = set()
    for dep_info in dep_tree:
        file_set.update(dep_info.files)
    return file_set


def compress_all(lib_list, base):
    base = os.path.expanduser(base)
    conda_path = conda_base + env_name


def copy_all(lib_list, base, compress=True):
    base = os.path.expanduser(base)
    conda_path = conda_base + env_name
    err_count = 0
    copy_count = 0
    all_count = len(lib_list)
    progress_count = 0
    if compress:
        if not os.path.exists(os.path.dirname(base)):
            os.makedirs(os.path.dirname(base))
        compress_files(conda_path, lib_list, base)
        return
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


def dump(package: str, exclude_list: List[str]):
    conda_env_name = (
        lambda: "base" if env_name == "" else os.path.split(env_name)[-1]
    )()
    print(
        f'dump package "{package}" in envirment "{conda_env_name}", exclude_list: {exclude_list}'
    )
    print(f'dump destination path: "{dump_path}"')
    req = DependReq(name=package)
    dep_info = search_dep(req)
    if not dep_info:
        print(
            f'ERROR: package "{package}" not found in conda envirment "{conda_env_name}", dump stop'
        )
        sys.exit(1)
    ex = []
    for exclude in exclude_list:
        ex.append(DependReq(name=exclude))
    print(f"parsing dependent tree")
    dep_tree = dep(dep_info, ex)
    if print_tree:
        dep_tree.print_struct()
    if not dry_run:
        print(f"start copying file to {dump_path}")
        copy_all(get_lib(dep_tree), dump_path)


def restore(dump_file: str):
    conda_path = conda_base + env_name
    dump_file = os.path.expanduser(dump_file)
    print(f"start decompress file {dump_file} to {conda_path}")
    if not decompress_files(dump_file, conda_path):
        print(f"dump file {dump_file} not found")
        sys.exit(1)


def main():
    import argparse

    func_list = ["dump", "restore"]
    parser = argparse.ArgumentParser(prog="conda-dump")
    parser.add_argument("subcommand", type=str, choices=func_list)
    parser.add_argument("package", type=str, help="specify a package to dump")
    parser.add_argument(
        "-n", "--conda-env", type=str, dest="conda_env", help="specify a envirment name"
    )
    parser.add_argument(
        "-c",
        "--conda-path",
        type=str,
        dest="conda_path",
        help="specify a conda base path",
    )
    parser.add_argument(
        "-e", "--exclude", action="append", type=str, help="exclude exist package"
    )
    parser.add_argument(
        "-d", "--dump-path", dest="dump_path", help="dump destination directory"
    )
    parser.add_argument(
        "-t",
        "--print-tree",
        action="store_true",
        dest="print_tree",
        help="print dependent tree",
    )
    parser.add_argument(
        "--dry-run", action="store_true", dest="dry_run", help="dry run"
    )
    args = parser.parse_args()
    global conda_base, env_name, print_tree, dry_run, dump_path
    if args.conda_path:
        conda_base = args.conda_path
    conda_base = os.path.expanduser(conda_base).replace("\\", "/")
    if not os.path.exists(conda_base):
        print(
            f"conda path not found in default path {conda_base}, please specify another"
        )
        sys.exit(1)
    if args.conda_env:
        env_name = "/envs/" + args.conda_env
    print_tree = args.print_tree
    dry_run = args.dry_run
    if args.dump_path:
        dump_path = args.dump_path
    dump_path = os.path.expanduser(dump_path).replace("\\", "/")

    print(f'working on conda path: "{conda_base}"')
    if args.subcommand == "dump":
        dump(args.package, args.exclude)
    elif args.subcommand == "restore":
        restore(args.package)


if __name__ == "__main__":
    main()
