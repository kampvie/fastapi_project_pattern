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

Folder, files need for deploy with AWS CodeDeploy

| Location         |
| ---------------- |
| scripts/aws/*.sh |
| ./appspec.yml    |

Using remote mongodb or(and) postgres by providing these value in ```docker-compose.yml```

- REMOTE_MONGO_URL
- REMOTE_POSTGRES_URL
  
Using sendgrid and cloudinary by providing these value also:

- SENDGRID_API_KEY
- CLOUDINARY_URL

Set up values in `project.settings`

| Variable name | Description                  | Default                                             |
| ------------- | ---------------------------- | --------------------------------------------------- |
| PROJECT_NAME  | Name of the project          | FastAPI-project-pattern                             |
| GIT_SSH_REPO  | SSH repo url                 | git@github.com:Sang2306/FastAPI-project-pattern.git |
| SERVICE_NAME  | Name of systemd unit service | deploy_$PROJECT_NAME                                |
| PORT          | Port to run service          | 2306                                                |
