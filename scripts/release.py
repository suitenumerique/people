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


def update_helm_files(path):
    sys.stdout.write("Update helm files...\n")
    with open(path, 'r') as file:
        lines = file.readlines()
        for index, line in enumerate(lines):
            if "tag:" in line:
                lines[index] = re.sub(r'\"(.*?)\"', f'"v{version}"', line)
    with open(path, 'w+') as file:
        file.writelines(lines)


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


def deployment_part(version):
    """ Update helm file of preprod on deployment repository numerique-gouv/lasuite-deploiement
    """
    # Move to lasuite-deploiement repository
    try:
        os.chdir('../lasuite-deploiement')
    except FileNotFoundError:
        sys.stdout.write("\033[1;31m[Error] You must have a clone of https://github.com/numerique-gouv/lasuite-deploiement\x1b[0m")
        sys.stdout.write("\033[0;32mPlease clone it and re-run script with option --only-deployment-part\x1b[0m")
        sys.stdout.write("  >>> python scripts/release.py --only-deployment-part \x1b[0m")
    else:
        run_command("git checkout main", shell=True)
        run_command("git pull", shell=True)
        deployment_branch = f"regie/{version}/preprod"
        run_command(f"git checkout -b {deployment_branch}", shell=True)
        run_command("git pull --rebase origin main", shell=True)
        path = f"manifests/regie/env.d/preprod/values.desk.yaml.gotmpl"
        update_helm_files(path)
        run_command(f"git add {path}", shell=True)
        message = f"""🔖(regie) bump preprod version to {version}"""
        run_command(f"git commit -m '{message}'", shell=True)
        confirm = input(f"""\033[0;32m
### DEPLOYMENT ###
NEXT COMMAND on lasuite-deploiement repository: 
    >> git push origin {deployment_branch}
Continue ? (y,n) 
\x1b[0m""").strip()
        if confirm == 'y':
            run_command(f"git push origin {deployment_branch}", shell=True)
        sys.stdout.write(f"""\033[1;34m
PLEASE DO THE FOLLOWING INSTRUCTIONS: 
--> Please submit PR {deployment_branch} and merge code to main [https://github.com/numerique-gouv/lasuite-deploiement]
\x1b[0m""")


def project_part(version, kind):
    """Manage only la regie part with update of CHANGELOG, version files and tag"""
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
    confirm = input(f"""\033[0;32m
### RELEASE ###
NEXT COMMAND on current repository:
    >> git push origin {branch_to_release}
Continue ? (y,n)
\x1b[0m""").strip()
    if confirm == 'y':
        run_command(f"git push origin {branch_to_release}", shell=True)
    sys.stdout.write(f"""
\033[1;34mPLEASE DO THE FOLLOWING INSTRUCTIONS:
--> A github action will download last translations from crowdin and create a commit to merge into the release branch.
    Please wait for this and merge this translations commit into the release branch {branch_to_release}.
--> Then please submit PR {branch_to_release} and merge code to main [https://github.com/suitenumerique/people/]
--> Then do:
    >> git checkout main
    >> git pull
    >> git tag v{version} 
    >> git push origin v{version} 
--> Please check and wait for the docker image v{version} to be published here:
 - https://hub.docker.com/r/lasuite/people-backend/tags 
 - https://hub.docker.com/r/lasuite/people-frontend/tags
--> Now please generate release on github interface for the current tag v{version}
 \x1b[0m""")


if __name__ == "__main__":
    version, kind = None, None
    while not version:
        version = input("Enter your release version:").strip()
    while kind not in RELEASE_KINDS:
        kind = input("Enter kind of release (p:patch, m:minor, mj:major):").strip()
    if "--only-deployment-part" not in sys.argv:
        project_part(version, kind)
    deployment_part(version)
