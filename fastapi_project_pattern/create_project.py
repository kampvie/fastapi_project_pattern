import git
import os
import subprocess
import shutil
import shlex
import re
from pathlib import Path
from fileinput import FileInput
from distutils.dir_util import copy_tree

CWD = Path(__file__).parent

LOCAL_DIR = Path(__file__).parent / "temp"

GIT_REPO = LOCAL_DIR / ".git"


def remove_local_dir():
    if os.path.isdir(LOCAL_DIR.as_posix()):
        shutil.rmtree(LOCAL_DIR.as_posix())


remove_local_dir()

REMOTE_REPO = "https://github.com/kampvie/fastapi_project_pattern.git"

BRANCH = "main"


def start_creation(path: Path = None, use_local_posgres: bool = False, use_remote_postgres_url: bool = False,
    use_circle_ci: bool = False, use_gitlab_ci: bool = False
):
    """Create a project template
    Args:
        path (Path): Location a project should be placed once created
        use_local_posgres (bool): Whether use local PostgreSQL or not
        use_remote_postgres_url (bool): Use remote PostgreSQL or not
        use_circle_ci (bool): Using Circle CI/CD
        use_gitlab_ci (bool): Using Gitlab CI/CD
    """
    if not path:
        raise ValueError("path parameter is required")
    # Clone git repo into local
    git.Repo.clone_from(REMOTE_REPO, LOCAL_DIR.as_posix(), branch=BRANCH)

    cmd = shlex.split("openssl rand -hex 32")

    SECRET_KEY = subprocess.run(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8").strip()

    VARS = {
        # KEY: [DefaultValue, Promtline, Required, ValidateRegrexPattern, Type]
        'PROJECT_NAME': ["", "Project name >>> ", True, None, str],

        'PROJECT_LOGO_URL': ["", "Project logo url >>> ", True, None, str],

        'PROJECT_GIT_SSH_REPO': ["", "SSH git repository >>> ", True, None, str],

        'PROJECT_TITLE': ["", "Title >>> ", True, None, str],

        'PROJECT_SECRET_KEY': [SECRET_KEY, f"Secret[Default: {SECRET_KEY}] >>> ", False, None, str],

        'PROJECT_DESCRIPTION': [None, "Description >>> ", True, None, str],

        'PORT': ["2306", "Port to run [0-65536](Default: 2306) >>> ", False, None, str],

        'CLOUDINARY_URL': ["None", "CLOUDINARY_URL(Optional) >>> ", False, None, str],

        'SENDGRID_API_KEY': ["None", "SENDGRID_API_KEY(Optional) >>> ", False, None, str],

        'LOCAL_POSTGRES_USER': ["None", "POSTGRES_USER[Optional] >>> ", False, None, str],

        'LOCAL_POSTGRES_DB': ["None", "POSTGRES_DB[Optional] >>> ", False, None, str],

        'LOCAL_POSTGRES_PASSWORD': ["None", "POSTGRES_PASSWORD[Optional] >>> ", False, None, str],

        'REMOTE_POSTGRES_URL': ["None", "REMOTE_POSTGRES_URL[Optional] >>> ", False, None, str],

        'MONGO_INITDB_ROOT_USERNAME': ["mongo", "MONGO_INITDB_ROOT_USERNAME(Default: mongo) >>> ", False, None, str],

        'MONGO_INITDB_ROOT_PASSWORD': ["mongo", "MONGO_INITDB_ROOT_PASSWORD >>> ", True, None, str],

        'MONGO_DATABASE_NAME': ["master", "MONGO_DATABASE_NAME(Default: master) >>>", True, None, str],

        'REMOTE_MONGO_URL': ["None", "REMOTE_MONGO_URL >>> ", True, None, str],

        'RABBITMQ_DEFAULT_USER': ["rabbit", "RABBITMQ_DEFAULT_USER(Default: rabbit) >>> ", False, None, str],

        'RABBITMQ_DEFAULT_PASS': ["rabbit", "RABBITMQ_DEFAULT_PASS >>> ", True, None, str],
    }

    # Check use_local_posgres flag. If it was not used then remove out of VARS 
    if not use_local_posgres:
        del VARS['LOCAL_POSTGRES_USER']
        del VARS['LOCAL_POSTGRES_DB']
        del VARS['LOCAL_POSTGRES_PASSWORD']
    if not use_remote_postgres_url:
        del VARS['REMOTE_POSTGRES_URL']

    def is_valid(v, text):
        # Check if text is empty but this field is required
        # So with that said it's not valid
        if len(text) == 0 and v[2]:
            return False
        # TODO Check regrex to validate pattern
        return True

    for k, v in VARS.items():
        while True:
            text = input(v[1]).strip()
            # Project name is not allowed contains spaces
            if k == "PROJECT_NAME" and re.search(r"\s", text):
                continue
            if is_valid(v, text):
                v[0] = text or v[0]
                break

    def replace(file_path: Path, text: str, subs: str, flags=0):
        """Replace content in a file
        """
        # Opening file using FileInput
        with FileInput(file_path.as_posix(), inplace=True) as f:
            for line in f:
                print(line.replace(text, subs), end='')

    # Remove .git in temp repo
    shutil.rmtree(GIT_REPO.as_posix())

    def change_files(path: Path):
        for file in os.listdir(path.as_posix()):
            _path = path / file
            if os.path.isfile(_path.as_posix()):
                for k, v in VARS.items():
                    replace(_path, "{{" + k + "}}", VARS[k][0])
                # Check to uncomment codeblock
                if use_local_posgres:
                    replace(_path, "#_p ", "")
            elif os.path.isdir(_path):
                change_files(_path)

    # Call function to apply
    change_files(LOCAL_DIR)

    # Remove redunrant files, folders
    redundancies = [
        LOCAL_DIR / "pyproject.toml",
        LOCAL_DIR / "LICENSE",
        LOCAL_DIR / "README.md",
    ]

    if not use_gitlab_ci:
        redundancies.append(
            LOCAL_DIR / ".gitlab-ci.yml"
        )

    if not use_circle_ci:
        CIRCLE_CI = LOCAL_DIR / ".circleci"
        shutil.rmtree(CIRCLE_CI.as_posix())

    for _path in redundancies:
        os.remove(_path.as_posix())

    FASTAPI_PROJECT_PATTERN = LOCAL_DIR / "fastapi_project_pattern"
    shutil.rmtree(FASTAPI_PROJECT_PATTERN.as_posix())

    # Create project directory and put code in it
    PROJECT_PATH: Path = CWD / f'{VARS["PROJECT_NAME"][0]}'
    path = path / f'{VARS["PROJECT_NAME"][0]}'

    os.mkdir(PROJECT_PATH.as_posix())
    copy_tree(LOCAL_DIR.as_posix(), PROJECT_PATH.as_posix())

    os.mkdir(path.as_posix())
    copy_tree(PROJECT_PATH.as_posix(), path.as_posix())

    shutil.rmtree(PROJECT_PATH.as_posix())
    remove_local_dir()
