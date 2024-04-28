import time
import click
import multiprocessing as mp

from mlsgpt import api, core, tasks


@click.group()
def cli() -> None:
    pass


@cli.command()
def run_services():
    processes = [
        mp.Process(target=tasks.run_tasks),
        mp.Process(target=api.run_app),
    ]
    for p in processes:
        p.start()
        time.sleep(5)

    core.keep_alive(processes)


if __name__ == "__main__":
    cli(obj={})
