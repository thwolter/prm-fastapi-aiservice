#!/usr/bin/env python
import subprocess  # nosec

import typer
import uvicorn

from app.core.config import settings

cmd = typer.Typer(no_args_is_help=True)


@cmd.command(name='run')
def run():
    """run application"""
    uvicorn.run(app='app.main:app', reload=True, port=settings.APP_PORT, host=settings.APP_HOST)


@cmd.command(name='migrate')
def migrate():
    process = subprocess.Popen(['alembic', 'upgrade', 'head'], stdout=subprocess.PIPE, shell=False)  # nosec
    print(process.communicate()[0])


@cmd.command(name='makemigrations')
def makemigrations(
    msg: str = typer.Option('autogenerate', '--msg', '-m', help='message'),
):
    process = subprocess.Popen(
        ['alembic', 'revision', '--autogenerate', '-m', f'{msg}'],
        stdout=subprocess.PIPE,
        shell=False,
    )  # nosec
    print(process.communicate()[0])


@cmd.command(name='createuser')
def createuser():
    pass


@cmd.command(name='lint')
def lint():
    """Run ruff check --fix, ruff format, and isort on all files"""
    subprocess.run(['ruff', 'check', '--fix', '.'])
    subprocess.run(['ruff', 'format', '.'])
    subprocess.run(['isort', '.'])


if __name__ == '__main__':
    cmd()
