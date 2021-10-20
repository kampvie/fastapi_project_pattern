import git
import os
import subprocess
import shutil
import shlex
from pathlib import Path
from fileinput import FileInput

LOCAL_DIR = Path(__file__).parent / "temp"

GIT_REPO = LOCAL_DIR / ".git"

if os.path.isdir(LOCAL_DIR.as_posix()):
    shutil.rmtree(LOCAL_DIR.as_posix())

REMOTE_REPO = "https://github.com/kampvie/fastapi-project-pattern.git"

BRANCH = "main"

def start_creation():
    # Clone git repo into local
    git.Repo.clone_from(REMOTE_REPO, LOCAL_DIR.as_posix(), branch=BRANCH)

    cmd = shlex.split("openssl rand -hex 32")

    SECRET_KEY = subprocess.run(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode("utf-8")

    VARS = {
        # KEY: [DefaultValue, Promtline, Required, ValidateRegrexPattern, Type]
        'PROJECT_NAME': [None, "Project name >>> ", True, None, str],
        'PROJECT_GIT_SSH_REPO': [None, "SSH git repository >>> ", True, None, str],
        'PROJECT_TITLE': [None, "Title >>> ", True, None, str],
        'PROJECT_SECRET_KEY': [SECRET_KEY, f"Secret[Default: {SECRET_KEY}] >>> ", False, None, str],
        'PROJECT_DESCRIPTION': [None, "Description >>> ", True, None, str],
        'PORT': [2306, "Port to run [0-65536](Default: 2306) >>> ", True, None, int],
        'CLOUDINARY_URL': [None, "CLOUDINARY_URL(Optional) >>> ", False, None, str],
        'SENDGRID_API_KEY': [None, "SENDGRID_API_KEY(Optional) >>> ", False, None, str],
        'REMOTE_MONGO_URL': [None, "REMOTE_MONGO_URL(Optional) >>> ", False, None, str],
        'REMOTE_POSTGRES_URL': [None, "REMOTE_POSTGRES_URL[Optional]: ", False, None, str],
        'MONGO_INITDB_ROOT_USERNAME': ["mongo", "MONGO_INITDB_ROOT_USERNAME(Default: mongo) >>> ", False, None, str],
        'MONGO_INITDB_ROOT_PASSWORD': ["mongo", "MONGO_INITDB_ROOT_PASSWORD(Default: mongo) >>> ", False, None, str],
        'RABBITMQ_DEFAULT_USER': ["rabbit", "RABBITMQ_DEFAULT_USER(Default: rabbit) >>> ", False, None, str],
        'RABBITMQ_DEFAULT_PASS': ["rabbit", "RABBITMQ_DEFAULT_PASS(Default: rabbit) >>> ", False, None, str],
    }

    for k, v in VARS.items():
        # Read from input and check validation
        v[0] = input(v[1]).strip()
        is_invalid = False
        if len(v[0]) == 0 and v[2]:
            is_invalid = True
        # TODO Check regrex for validate user input
        while is_invalid:
            v[0] = input(v[1]).strip()


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
                    replace(_path, "{" + k + "}", VARS[k][0])
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
    for _path in redundancies:
        os.remove(_path.as_posix())
