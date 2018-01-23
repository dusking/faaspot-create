#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import tempfile
from collections import namedtuple
from contextlib import contextmanager

import utils
from .aws import AWS
from .command import Command

logger = logging.getLogger(__name__)

Deployment = namedtuple('Deployment', ['repo', 'config', 'zip'], verbose=False)
FAASPOT_FOLDER = '.faaspot'


class Apps(Command):
    def __init__(self, *args, **kwargs):
        super(Apps, self).__init__(*args, **kwargs)

    def list(self):
        return AWS().list_functions()

    def create(self, repo_url, branch):
        logger.info('Creating FaaS app for repo: {0}:{1}..'.format(repo_url, branch))
        with self._create_deployment(repo_url, branch) as deployment:
            functions = utils.get_configured_functions(deployment.config)
            if len(functions) == 0:
                logger.warning('Missing configured functions')
                return "Missing configured functions"
            for name, info in functions.iteritems():
                logger.info('Creating function: {0}'.format(name))
                repo_name = os.path.basename(repo_url)
                AWS().create_function(name, repo_name, info['method'], deployment.zip)
        return "Done"

    def update(self, repo_url, branch):
        logger.info('Updating FaaS app for repo: {0}:{1}..'.format(repo_url, branch))
        with self._create_deployment(repo_url, branch) as deployment:
            functions = utils.get_configured_functions(deployment.config)
            if len(functions) == 0:
                logger.warning('Missing configured functions')
                return "Missing configured functions"
            for name in functions:
                logger.info('Updating function: {0}'.format(name))
                AWS().update_function(name, deployment.zip)
        return "Done"

    def delete(self, function_name):
        return AWS().delete_function(function_name)

    def run(self, function_name, parameters):
        data = {x[0].split("=")[0]: x[0].split("=")[1] for x in parameters}
        logger.info('Going to run {0}, with: {1}'.format(function_name, data))
        return AWS().invoke_function(function_name, data)

    @staticmethod
    @contextmanager
    def _create_deployment(repo_url, branch):
        # create temp folder
        prefix = '{0}_'.format(time.strftime("%Y%m%d"))
        temp_build_folder = tempfile.mkdtemp(prefix=prefix)

        try:
            # clone git repo
            logger.info('Cloning repo..')
            clone_folder = os.path.join(temp_build_folder, 'repo')
            repo_path = utils.clone_repo(repo_url, destination=clone_folder, branch=branch)
            faaspot_folder = os.path.join(repo_path, FAASPOT_FOLDER)
            faaspot_config = os.path.join(faaspot_folder, 'faaspot.yml')
            logger.debug('Repo cloned to: {0}'.format(clone_folder))

            # prepare deployment folder
            logger.debug('Creating deployment folder..')
            deployment_folder = os.path.join(temp_build_folder, 'deploy')
            utils.makedir(deployment_folder)
            logger.debug('Deployment folder created: {0}'.format(deployment_folder))

            # copy modules from faaspot folder to the deployment folder
            logger.info('Copying config files into deployment folder..')
            utils.copy_files(faaspot_folder, deployment_folder)

            # build package into the deployment folder
            logger.info('Installing dependencies..')
            utils.install_libraries(repo_path, deployment_folder)

            # create a zip from the
            logger.info('Packaging it..')
            deployment_zip = os.path.join(temp_build_folder, 'deploy.zip')
            utils.zip_dir(deployment_folder, deployment_zip)
            logger.info('Zip file created: {0}'.format(deployment_zip))

            yield Deployment(repo_path, faaspot_config, deployment_zip)
        finally:
            utils.remove_dir(temp_build_folder)
