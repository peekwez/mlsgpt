import time
import click
import multiprocessing as mp

from mlsgpt import tasks


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    "--env-file",
    default=".env",
    type=click.Path(exists=True),
    help="Path to the environment file",
)
def run_services(env_file: str):
    processes = [
        mp.Process(target=tasks.result_consumer, args=(env_file,)),
        mp.Process(target=tasks.extract_consumer, args=(env_file,)),
    ]
    for p in processes:
        p.start()
        time.sleep(3)

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        [p.terminate() for p in processes]


if __name__ == "__main__":
    cli(obj={})
