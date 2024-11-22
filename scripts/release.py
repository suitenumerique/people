# pylint: disable=line-too-long

import datetime
import os
import re
import sys

from utils import run_command


RELEASE_KINDS = {'p': 'patch', 'm': 'minor', 'mj': 'major'}


def update_files(version):
    """Update all files needed with new release version"""
    # pyproject.toml
    sys.stdout.write("Update pyproject.toml...\n")
    path = "src/backend/pyproject.toml"
    with open(path, 'r') as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if line.startswith("version = "):
                lines[index] = re.sub(r'\"(.*?)\"', f'"{version}"', line)
    with open(path, 'w+') as file:
        file.writelines(lines)

    # helm files
    sys.stdout.write("Update helm files...\n")
    for env in ["preprod", "production"]:
        path = f"src/helm/env.d/{env}/values.desk.yaml.gotmpl"
        with open(path, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if "tag:" in line:
                    lines[index] = re.sub(r'\"(.*?)\"', f'"v{version}"', line)
        with open(path, 'w+') as file:
            file.writelines(lines)

    # frontend package.json
    sys.stdout.write("Update package.json...\n")
    files_to_modify = []
    filename = "package.json"
    for root, _dir, files in os.walk("src/frontend"):
        if filename in files and "node_modules" not in root and ".next" not in root:
            files_to_modify.append(os.path.join(root, filename))

    for path in files_to_modify:
        with open(path, 'r') as file:
            lines = file.readlines()
            for index, line in enumerate(lines):
                if "version" in line:
                    lines[index] = re.sub(r'"version": \"(.*?)\"', f'"version": "{version}"', line)
        with open(path, 'w+') as file:
            file.writelines(lines)
    return


def update_changelog(path, version):
    """Update changelog file with release info
    """
    sys.stdout.write("Update CHANGELOG...\n")
    with open(path, 'r') as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if "## [Unreleased]" in line:
                today = datetime.date.today()
                lines.insert(index + 1, f"\n## [{version}] - {today}\n")
            if line.startswith("[unreleased]"):
                last_version = lines[index + 1].split("]")[0][1:]
                new_unreleased_line = line.replace(last_version, version)
                new_release_line = lines[index + 1].replace(last_version, version)
                lines[index] = new_unreleased_line
                lines.insert(index + 1, new_release_line)
                break

    with open(path, 'w+') as file:
        file.writelines(lines)


def prepare_release(version, kind):
    sys.stdout.write('Let\'s go to create branch to release\n')
    branch_to_release = f"release/{version}"
    run_command(f"git checkout -b {branch_to_release}", shell=True)
    run_command("git pull --rebase origin main", shell=True)

    update_changelog("CHANGELOG.md", version)
    update_files(version)

    run_command("git add CHANGELOG.md", shell=True)
    run_command("git add src/", shell=True)
    message = f"""🔖({RELEASE_KINDS[kind]}) release version {version}

    Update all version files and changelog for {RELEASE_KINDS[kind]} release."""
    run_command(f"git commit -m '{message}'", shell=True)
    confirm = input(f"\nNEXT COMMAND: \n>> git push origin {branch_to_release}\nContinue ? (y,n) ")
    if confirm == 'y':
        run_command(f"git push origin {branch_to_release}", shell=True)
    sys.stdout.write(f"""
    PLEASE DO THE FOLLOWING INSTRUCTIONS:
    --> Please submit PR and merge code to main 
    --> Then do:
    >> git checkout main
    >> git pull
    >> git tag v{version} 
    >> git push origin v{version} 
    --> Please check and wait for the docker image v{version} to be published here: https://hub.docker.com/r/lasuite/people-backend/tags
    >> git tag -d preprod
    >> git tag preprod
    >> git push -f origin preprod
    --> Now please generate release on github interface for the current tag v{version}
""")


if __name__ == "__main__":
    version, kind = None, None
    while not version:
        version = input("Enter your release version:")
    while kind not in RELEASE_KINDS:
        kind = input("Enter kind of release (p:patch, m:minor, mj:major):")
    prepare_release(version, kind)
