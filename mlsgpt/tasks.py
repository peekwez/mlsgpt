import json
import time
import boto3
from typing import Callable
from mlsgpt import core, logger
from mlsgpt.db import models, store


DELAY_SECONDS = 120

sqs = boto3.client("sqs")


def create_sqs_queue(queue_name, delay_seconds=0):
    response = sqs.create_queue(
        QueueName=queue_name, Attributes={"DelaySeconds": str(delay_seconds)}
    )
    return response["QueueUrl"]


file_queue_url = create_sqs_queue("mls_process_file")
result_queue_url = create_sqs_queue("mls_process_result", delay_seconds=DELAY_SECONDS)


def publish_message(queue_url, message_body, delay_seconds=0):
    sqs.send_message(
        QueueUrl=queue_url, MessageBody=message_body, DelaySeconds=delay_seconds
    )


def process_file(
    message_body: str,
    log: logger.logging.Logger,
    *,
    writer: store.DataWriter | None = None,
) -> None:
    file = models.FileInfo.model_validate_json(message_body)
    log.info(f"File id: {file.id} received")

    images, mime_type = core.prepare_request(file.download_link, file.mime_type)
    size = len(images)
    log.info(f"File id: {file.id} split into {size} pages")

    for i, image in enumerate(images):
        page = models.Page(id=file.id, num=i + 1, content=image, mime_type=mime_type)
        ret = core.extract_data(page.content, page.mime_type)
        _id = ret["result"]["request_id"]
        if ret["OK"]:
            log.info(f"Page id: {page.id} page: {page.num}/{size} queued")
            publish_message(
                result_queue_url, json.dumps({"id": _id}), delay_seconds=DELAY_SECONDS
            )
            log.info(
                f"Page id: {page.id} page: {page.num}/{size} result: {_id[:8]}... published"
            )
        else:
            log.error(f"Page id: {page.id} page: {page.num} failed")
            log.error(f"Error: {ret['result']['error']}")
        time.sleep(0.5)


def process_result(
    message_body: str,
    log: logger.logging.Logger,
    *,
    writer: store.DataWriter | None = None,
) -> None:

    req = models.Result.model_validate_json(message_body)
    short_id = req.id[:8]
    log.info(f"Result id: {short_id}... received")

    ret = core.fetch_result(req.id)
    status = ret["result"]["status"]
    

    if status in ["QUEUED", "RUNNING"]:
        log.info(f"Result id: {short_id}... status={status}")
        publish_message(
            result_queue_url, req.model_dump_json(), delay_seconds=DELAY_SECONDS
        )
    elif status == "COMPLETED":
        log.info(f"Result id: {short_id}... success")
        writer.save(ret["result"])
        log.info(f"Result id: {short_id}... saved")
    elif status == "FAILED":
        log.error(f"Error: {ret["result"]["error"]}")
        log.error(f"Result id: {short_id}... failed")


def poll_sqs_messages(
    queue_url,
    process_message_func: Callable,
    log: logger.logging.Logger,
    *,
    writer: store.DataWriter | None = None,
):
    sqs = boto3.client("sqs")
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20
        )
        messages = response.get("Messages", [])
        for message in messages:
            process_message_func(message["Body"], log, writer=writer)
            sqs.delete_message(
                QueueUrl=queue_url, ReceiptHandle=message["ReceiptHandle"]
            )


def run_tasks():
    log = logger.get_logger("task-service")
    writer = store.DataWriter(log=log)

    from threading import Thread

    Thread(
        target=poll_sqs_messages,
        args=(result_queue_url, process_result, log),
        kwargs=dict(writer=writer),
    ).start()
    log.info("Result queue listener started")
    time.sleep(2)

    Thread(target=poll_sqs_messages, args=(file_queue_url, process_file, log)).start()
    log.info("File queue listener started")
    time.sleep(2)

    log.info("Task service started")
    core.keep_alive()
