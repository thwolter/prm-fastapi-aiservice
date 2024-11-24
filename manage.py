#!/usr/bin/env python
import importlib
import inspect
import pkgutil
import subprocess  # nosec
from pathlib import Path

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


@cmd.command(name='list-prompts')
def list_prompts():
    """List all prompt names from services"""
    services = []
    prompt_names = []

    # Discover and import all service modules
    package_dir = Path(__file__).resolve().parent / 'app' / 'risk'
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name.endswith('service'):
            module = importlib.import_module(f'app.risk.{module_name}')
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if name.endswith('Service'):
                    services.append(obj)

    # Collect prompt names from services
    for service in services:
        if hasattr(service, 'prompt_name'):
            prompt_names.append(service.prompt_name)
        if hasattr(service, 'prompt_name_category') and hasattr(service, 'prompt_name_categories'):
            prompt_names.append(service.prompt_name_category)
            prompt_names.append(service.prompt_name_categories)

    for prompt in prompt_names:
        print(prompt)


if __name__ == '__main__':
    cmd()
