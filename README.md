[![<ORG_NAME>](https://circleci.com/gh/kampvie/fastapi-project-pattern.svg?style=shield)](https://circleci.com/gh/kampvie/fastapi-project-pattern/?branch=main)

# FastAPI project pattern with tools

* FastAPI
* Celery
* RabbitMQ
* MongoDB(PyMongo)
* PostgreSQL(SQL Alchemmy, Alembic)
* Web Socket
* Send email with Sendgrid
* ![logo](https://cloudinary-res.cloudinary.com/image/upload/c_scale,h_24,w_72/cloudinary_logo_for_white_bg.png) [Cloudinary](https://cloudinary.com/)

**Deployments**

| Location             | CI/CD          |
| -------------------- | -------------- |
| .gitlab-ci.yml       | Gitlab CI/CD   |
| .circleci/config.yml | CircleCI       |
| ./scripts/aws/*.sh   | AWS CodeDeploy |
| ./scripts/vps/*.sh   | Manual Deploy  |

**Installation**

`pip install fastapi_project_pattern`

```python
from pathlib import Path

from fastapi_project_pattern import start_creation

# See help(start_creation) for more
start_creation(Path.cwd())
```
