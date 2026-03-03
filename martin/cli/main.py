import click
from martin.cli.dev import run_dev
from martin.cli.scaffold import create_project


@click.group()
def cli():
    """
    MARTIN CLI
    """
    pass


@cli.command()
@click.option("--port", default=309, help="Puerto del servidor (default: 309)")
@click.option("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
def dev(port, host):
    """
    Inicia servidor de desarrollo.
    """
    run_dev(host=host, port=port)


@cli.command()
@click.argument("name")
def new(name):
    """
    Crea un nuevo proyecto MARTIN.
    """
    create_project(name)
