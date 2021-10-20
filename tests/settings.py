from multiprocessing import Process

import uvicorn


def run_server():
    uvicorn.run("app.main:app", host='0.0.0.0', port=2306)


proc = Process(target=run_server, args=(), daemon=True)
