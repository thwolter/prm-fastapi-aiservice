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


@cmd.command(name='list-prompts')
def list_prompts():
    """List all prompt names from services"""
    import inspect

    from app.services import services

    prompt_names = []
    for name, obj in inspect.getmembers(services, inspect.isclass):
        if hasattr(obj, 'prompt_name'):
            prompt_names.append(obj.prompt_name)
        elif hasattr(obj, 'prompt_name_category') and hasattr(obj, 'prompt_name_categories'):
            prompt_names.append(obj.prompt_name_category)
            prompt_names.append(obj.prompt_name_categories)

    for prompt in prompt_names:
        print(prompt)


if __name__ == '__main__':
    cmd()
