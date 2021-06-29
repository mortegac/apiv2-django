import asyncio
import importlib
import inspect
import logging
import os

from django.contrib.auth.models import User
from django.db.models import Model
from mixer.backend.django import mixer

from breathecode.authenticate.management.commands.create_roles import Command

logger = logging.getLogger(__name__)

PROJECT = 'breathecode'
MODULES = [
    'admissions',
    # 'assessment',
    'assignments',
    'authenticate',
    'certificate',
    'events',
    'feedback',
    'freelance',
    'marketing',
    'media',
    'monitoring',
    'notify',
]


def clean():
    cleaned = ['User']

    User.objects.all().delete()

    for forder in MODULES:
        path = f'{PROJECT}.{forder}.models'
        module = importlib.import_module(path)
        models = []

        for x in dir(module):
            CurrentModel = getattr(module, x)
            if not inspect.isclass(CurrentModel):
                continue

            if not issubclass(CurrentModel, Model):
                continue

            if (hasattr(CurrentModel, 'Meta')
                    and hasattr(CurrentModel.Meta, 'abstract')):
                continue

            models.append(CurrentModel)

        for CurrentModel in models:
            model_name = CurrentModel.__name__

            if model_name in cleaned:
                continue

            logger.info(f'{model_name} was cleaned')
            CurrentModel.objects.all().delete()
            cleaned.append(model_name)


def load_fixtures():
    for forder in MODULES:
        path = f'{PROJECT}/{forder}/fixtures'

        for root, dirs, files in os.walk(path):
            for name in files:
                if name.startswith('dev_') and name.endswith('.json'):
                    logger.info(f'Load {path}/{name}')
                    os.system(  # noqa: S605
                        f'python manage.py loaddata {path}/{name}')


def load_roles():
    command = Command()
    command.handle()

    logger.info('Roles loaded')


def reset():
    clean()
    load_fixtures()


def get_model(model_name):
    modules = MODULES
    found = []

    if '.' in model_name:
        parts = model_name.split('.')
        if len(parts) != 2:
            raise Exception('Bad model name format')

        modules = [parts[0]]
        model_name = parts[1]

    if model_name == 'User':
        found.append(User)

    for forder in modules:
        path = f'{PROJECT}.{forder}.models'
        module = importlib.import_module(path)

        if not hasattr(module, model_name):
            continue

        model = getattr(module, model_name)

        if not inspect.isclass(model):
            continue

        if not issubclass(model, Model):
            continue

        if (hasattr(model, 'Meta') and hasattr(model.Meta, 'abstract')):
            continue

        found.append(model)

    if not found:
        raise Exception('Model not found')

    if len(found) > 1:
        raise Exception(
            'Exist many app with the same model name, use `app.model` syntax')

    return found[0]


def clean_model(model_name):
    Model = get_model(model_name)
    Model.objects.all().delete()


def generate_model(index, data, how_many=1):
    status = 'done'
    pks = []

    try:
        model_name = data.pop('$model')
        Model = get_model(model_name)
        for element in mixer.cycle(how_many).blend(Model, **data):
            pks.append(element.pk)

    except Exception as e:
        status = str(e)

    return {
        'pks': pks,
        'model': model_name,
        'index': index,
        'status_text': status,
    }


def generate_models(step, how_many=1):
    result = []

    for index, data in enumerate(step):
        current_result = generate_model(index, data, how_many)
        result.append(current_result)

    return result
