import time
import click
import multiprocessing as mp

from mlsgpt import api, core, tasks, apiv2


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("-n", "--ngrok", is_flag=True, help="Start ngrok tunnel", default=False)
@click.option("-a", "--api-version", type=click.Choice(["v1", "v2"]), default="v2")
def run_services(api_version:str, ngrok:bool) -> None:
    if api_version == "v1":
        processes = [
            mp.Process(target=tasks.run_tasks),
            mp.Process(target=api.run_app, args=(ngrok,)),
        ]
    elif api_version == "v2":
        processes = [mp.Process(target=apiv2.run_app, args=(ngrok,))]

    for p in processes:
        p.start()
        time.sleep(5)

    core.keep_alive(processes)

