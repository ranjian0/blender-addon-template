#!/usr/bin/python3
#
# Generate an addon release archive. For repeatability, the timestamp
# and contents for each file are taken from the last commit affecting
# that file.
#
# This script takes an arg identifying a specific commit (e.g. a tag)
# from which to generate the archive. For example, the command
#
#     ./make-release v1.0
#
# will make an archive for the commit tagged v1.0 (assuming it exists).
# This tag name will also be included in the created archive name.
import os
import sys
import pathlib
import shutil
import subprocess
import toml
import pathlib

REPO_FILES = (
    "src/",
)


def git(*args: str | bytes) -> bytes:
    try:
        return subprocess.check_output(("git",) + args, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError:
        return b""

def main() -> None:
    upto = git("describe", "--tags", "--abbrev=0").strip().decode()
    if not upto:
        print("Git repository has no tags, please create one!")
        return
    
    with open(pathlib.Path(__file__).parent.parent / "pyproject.toml") as f:
        config = toml.load(f)

    earliest = git("rev-list", "--reverse", upto).split(b"\n")[0].strip().decode()
    basename = config['project']['name']
    foldername = f"{basename}_{upto}"
    outfilename = f"{foldername}.zip"
    if pathlib.Path(outfilename).exists():
        os.remove(outfilename)

    # -- create zip dir
    zip_folder = (pathlib.Path() / basename)
    if zip_folder.exists():
        shutil.rmtree(str(zip_folder))
    zip_folder.mkdir()

    # -- get files
    for item in REPO_FILES:
        if item.endswith("/"):
            items = sorted(
                set(
                    line.rsplit("\t", 1)[1]
                    for line in git("log", "--raw", item).decode().split("\n")
                    if line.startswith(":")
                )
            )
        else:
            items = [item,]

        for filename in items:
            info = git("log", "--format=%ct:%H", "-n1", "%s..%s" % (earliest, upto), "--", filename).strip()
            if info == b"":
                continue

            _, commit_hash = info.split(b":")
            info = git("ls-tree", commit_hash, filename).strip()

            if info != b"":
                object_hash = info.split(b"\t")[0].split(b" ")[2].decode()
                object_contents = git("show", object_hash)

                relative_filename = pathlib.Path(filename).parts[1:]
                zip_path = zip_folder.joinpath(*relative_filename)

                # -- create subfolders if missing
                if not zip_path.parent.exists():
                    zip_path.parent.mkdir()

                with open(zip_path, 'wb') as file:
                    file.write(object_contents)

    if len(list(zip_folder.glob("**/*.py"))):
        shutil.make_archive(foldername, 'zip', base_dir=str(zip_folder))
        shutil.rmtree(str(zip_folder))
        sys.stdout.write("created archive: %s\n" % outfilename)
    else:
        shutil.rmtree(str(zip_folder))
        sys.stdout.write(f"Error: No files at tagged at {upto}")

if __name__ == '__main__':
    main()
