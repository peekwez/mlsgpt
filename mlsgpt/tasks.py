import os
import redis
import time
import concurrent.futures

from dotenv import load_dotenv


from mlsgpt import core
from mlsgpt import store
from mlsgpt import logger


def get_redis_client():
    host = os.environ.get("REDIS_HOST")
    port = os.environ.get("REDIS_PORT")
    return redis.Redis(host=host, port=port, db=0, decode_responses=True)


def extract_consumer(env_file: str):
    load_dotenv(env_file)
    log = logger.get_logger("extract-consumer")

    r = get_redis_client()
    log.info("Extract consumer started")
    extract_stream = "mls:extract"
    result_stream = "mls:result"

    while True:
        stream = r.xread({extract_stream: "$"}, count=10, block=1000)
        if stream:
            for _, message in stream[0][1]:
                download_link = message["download_link"]
                mime_type = message["mime_type"]
                request_ids = core.extract_data(download_link, mime_type)
                log.info(f"Batch extraction submitted for {download_link}")

                if request_ids:
                    for request_id in request_ids:
                        r.xadd(result_stream, {"request_id": request_id})
                        log.info(f"Added request_id: {request_id} to result stream")


def poll_result(request_id: str):
    while True:
        result = core.fetch_result(request_id)
        if not result:
            return (request_id, result)

        if result["status"] == "COMPLETED":
            return (request_id, result)

        time.sleep(30)


def result_consumer(env_file: str):
    load_dotenv(env_file)
    log = logger.get_logger("result-consumer")

    r = get_redis_client()
    log.info("Result consumer started")
    stream_name = "mls:result"

    result_store = store.StoreWriter()
    log.info("Result store started")

    while True:
        stream = r.xread({stream_name: "$"}, count=10, block=1000)
        if stream:
            print(len(stream[0][1]))
            with concurrent.futures.ThreadPoolExecutor(10) as executor:
                futures = []
                for _, message in stream[0][1]:
                    future = executor.submit(poll_result, message["request_id"])
                    futures.append(future)

                results = []
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

            for request_id, result in results:
                if not result:
                    log.error(f"Error for request_id: {request_id}")
                    continue

                result_store.save(result)
                log.info(f"Saved result for request_id: {request_id}")
