import time
import click
import multiprocessing as mp

from mlsgpt import tasks, api


@click.group()
def cli() -> None:
    pass


@cli.command()
def run_services():
    processes = [
        mp.Process(target=tasks.save_results),
        mp.Process(target=tasks.extract_data),
        mp.Process(target=tasks.split_pages),
        mp.Process(target=api.run_app),
    ]
    for p in processes:
        p.start()
        time.sleep(5)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        [p.terminate() for p in processes]


if __name__ == "__main__":
    cli(obj={})
