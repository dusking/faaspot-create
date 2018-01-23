import os
import sh
import glob
import time
import yaml
import shutil
import zipfile
import logging
import tempfile

logger = logging.getLogger(__name__)


def clone_repo(repo_url, destination=None, branch="master"):
    logger.info('cloning repo: `{0}`, branch: {1}..'.format(repo_url, branch))
    clone = sh.git.bake('clone', '--depth', '1', '-b', branch)
    prefix = '{0}_'.format(time.strftime("%Y%m%d"))
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    clone(repo_url, temp_dir)
    if destination:
        move = sh.mv.bake()
        move(temp_dir, destination)
    else:
        destination = temp_dir
    logger.debug('repo cloned into: `{0}`'.format(destination))
    return destination


def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def remove_dir(path):
    shutil.rmtree(path)


def install_libraries(repo_folder, serverless_folder):
    logger.info('installing repo..')
    pip_install = sh.pip.bake('install', '-t', serverless_folder, '--upgrade')
    error = pip_install(repo_folder).stderr
    if error:
        logger.warning('failed installing repo: {0}'.format(error))
    requirements = os.path.join(repo_folder, 'requirements.txt')
    if os.path.exists(requirements):
        logger.info('installing package requirements..')
        error = pip_install('-r', requirements).stderr
        if error:
            logger.warning('failed installing package requirements: {0}'.format(error))


def copy_files(source_folder, destination):
    name_pattern = '*'
    for item in glob.glob(os.path.join(source_folder, name_pattern)):
        if os.path.isfile(item):
            shutil.copy(item, destination)


def zip_dir(dir_to_zip, target_zip_path):
    zipf = zipfile.ZipFile(target_zip_path, 'w', zipfile.ZIP_DEFLATED)
    try:
        rootlen = len(dir_to_zip)
        for base, dirs, files in os.walk(dir_to_zip):
            for entry in files:
                fn = os.path.join(base, entry)
                zipf.write(fn, fn[rootlen:])
    finally:
        zipf.close()


def get_configured_functions(config_path):
    with open(config_path) as config_file:
        config = yaml.load(config_file.read())
    return config['functions']
