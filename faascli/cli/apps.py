#!/usr/bin/env python


def add_apps_args(subparsers):
    root_parser_name = 'apps'
    parser_functions = subparsers.add_parser('apps', help='Manages apps')
    apps = parser_functions.add_subparsers(help='Manage apps',  dest=root_parser_name)

    apps.add_parser('list', help='List functions in app')

    create = apps.add_parser('create', help='Create new functions for app')
    create.add_argument('-r', '--repo-url',
                        action="store",
                        dest="repo_url",
                        help='The url of the repo',
                        required=True)
    create.add_argument('-b', '--branch',
                        action="store",
                        help='The branch name',
                        required=True)

    update = apps.add_parser('update', help='Update existing functions for app')
    update.add_argument('-r', '--repo-url',
                        action="store",
                        dest="repo_url",
                        help='The url of the repo',
                        required=True)
    update.add_argument('-b', '--branch',
                        action="store",
                        help='The branch name',
                        required=True)

    delete = apps.add_parser('delete', help='Delete a function')
    delete.add_argument('-f', '--function-name',
                        action="store",
                        dest="function_name",
                        help='The function name to delete',
                        required=True)

    run = apps.add_parser('run', help='Run an existing function')
    run.add_argument('function_name',
                     action="store",
                     help='The function name to run')
    run.add_argument('-p', '--parameters',
                     action="append",
                     help='Function parameters, list of key=value',
                     nargs='*',
                     required=False)
    return root_parser_name
