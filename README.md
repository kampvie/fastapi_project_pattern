[![<ORG_NAME>](https://circleci.com/gh/kampvie/fastapi-project-pattern.svg?style=shield)](https://circleci.com/gh/kampvie/fastapi-project-pattern/?branch=main)

# FastAPI project pattern with tools

* FastAPI
* Celery
* RabbitMQ
* MongoDB
* Web Socket
* Send email with Sendgrid
* ![logo](https://cloudinary-res.cloudinary.com/image/upload/c_scale,h_24,w_72/cloudinary_logo_for_white_bg.png) [Cloudinary](https://cloudinary.com/)
* CircleCI
* GitlabCI/CD

**AWS CodeDeploy scripts**

| Location         |
| ---------------- |
| scripts/aws/*.sh |
| ./appspec.yml    |

**Deploy VPS scripts**

| Location              | CI/CD        |
| --------------------- | ------------ |
| scripts/vps/deploy.sh | Gitlab CI/CD |
| .circleci/config.yml  | CircleCI     |

**Installation**

`pip install fastapi_project_pattern`

```python

from fastapi_project_pattern import start_creation

start_creation()

```
