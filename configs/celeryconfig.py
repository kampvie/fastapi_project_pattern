from configs.settings import (DB_HOST, DB_PORT, SCHEDULE_DB_UNAME, SCHEDULE_DB_PWD, SCHEDULE_DB)

result_backend = f'mongodb://{SCHEDULE_DB_UNAME}:{SCHEDULE_DB_PWD}@{DB_HOST}:{DB_PORT}/schedule?authMechanism=SCRAM-SHA-256'
result_persistent = True
mongodb_backend_settings = {
    'database': SCHEDULE_DB,
    'taskmeta_collection': f'{SCHEDULE_DB}_taskmeta',
}
task_reject_on_worker_lost = True
