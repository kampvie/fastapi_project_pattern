from configs.settings import (DB_HOST, DB_PORT, MONGO_INITDB_ROOT_USERNAME, MONGO_INITDB_ROOT_PASSWORD)

result_backend = f'mongodb://{MONGO_INITDB_ROOT_USERNAME}:{MONGO_INITDB_ROOT_PASSWORD}@{DB_HOST}:{DB_PORT}'
result_persistent = True
mongodb_backend_settings = {
    'database': 'celery',
    'taskmeta_collection': f'celery_taskmeta',
}
task_reject_on_worker_lost = True