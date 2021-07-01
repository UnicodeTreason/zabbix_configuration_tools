#!/usr/bin/env python3
# Import pips
import argparse
import io
import json
import jsonschema
import os
import sys
from deepdiff import DeepDiff
from pyzabbix import ZabbixAPI
# Import personal modules
import lib.config as config
import lib.mylogger as mylogger
import lib.validation as data_validation

# Vars
MODULE = 'zct'
DIR_BASE = os.path.abspath(os.path.dirname(sys.path[0]))
DIR_ETC = f'{DIR_BASE}/etc'
DIR_VAR = f'{DIR_BASE}/var'


def parse_args():
    '''Load validation from files in specified dir

    Args:
        N/A

    Returns:
        dict: a dict of the arguments passed at runtime
    '''
    logger.debug(f'function start: {sys._getframe(  ).f_code.co_name}')

    # Need to hijack stderr to capture the "helpful" argparse output and hide it
    # TODO: Python v3.9 make use of https://docs.python.org/3/library/argparse.html#exit-on-error
    # Why:  Better error output on bad arguments for logs/running apps
    temp_stderr = io.StringIO()
    sys.stderr = temp_stderr

    try:
        parser = argparse.ArgumentParser(description='Zabbix Configuration Management')
        parser.add_argument('desired_state_dir', type=str, help='The dir in which the desired state of Zabbix is stored.')
        # Convert argparse Namespace into dict for easy use and JSON validation later
        return vars(parser.parse_args())
    except SystemExit as error:
        stderr_str = temp_stderr.getvalue()
        stderr_str_split = stderr_str.splitlines()
        logger.error(f'Argument Parse failed: {stderr_str_split[-1]}')
        sys.exit(error.code)
    finally:
        # Put stderr back to original config
        sys.stderr = sys.__stderr__


def find_json_files(base_dir):
    for entry in os.scandir(base_dir):
        if entry.is_file() and entry.name.endswith('.json'):
            yield f'{base_dir}/{entry.name}'
        elif entry.is_dir():
            yield from find_json_files(entry.path)
        else:
            print(f'Neither a file, nor a dir: {entry.path}')


def main(args: dict):
    logger.debug(f'function start: {sys._getframe(  ).f_code.co_name}')

    # Initialise validation and configuration
    logger.debug('Validation Load')
    validation = data_validation.load(f'{DIR_ETC}/validation', f'{MODULE}.*')

    logger.debug('Config Load')
    app_config = config.load(f'{DIR_ETC}/config/{MODULE}.config.json')

    logger.debug('Config Validate')
    jsonschema.validate(instance=app_config, schema=validation[f'{MODULE}.config.json'])
    logger.debug('Runtime Args Validate')
    jsonschema.validate(instance=args, schema=validation[f'{MODULE}.args.json'])

    zapi = ZabbixAPI(app_config['zabbix']['url'])
    zapi.login(app_config['zabbix']['username'], app_config['zabbix']['password'])
    logger.info(f'Connected to Zabbix API Version {zapi.api_version()}')

    # Get all root hostgroup and all nested host groups
    hostgroups = {}
    hostgroups_raw = zapi.hostgroup.get(search={'name': [app_config['zabbix']['root_group']]})
    # Reorganise into sortable dict
    for hostgroup in hostgroups_raw:
        hostgroups[hostgroup['name']] = hostgroup['groupid']

    # Process hostgroups in "alphabetical" order
    current_state = {}
    logger.info('Caching current state for comparison')
    for hostgroup in sorted(hostgroups.keys()):
        # Get templates in desired groups
        for template in zapi.template.get(groupids=hostgroups[hostgroup]):
            # Get template configuration
            api_params = {'templates': [template['templateid']]}
            result = zapi.configuration.export(format='json', options=api_params)
            json_data = json.loads(result)
            current_state[template['name']] = json_data

            # Determine cache location and prepare it
            template_filename = f'{DIR_VAR}/cache/{hostgroup.replace(app_config["zabbix"]["root_group"], "")}/{template["name"]}.json'
            os.makedirs(os.path.dirname(template_filename), exist_ok=True)
            with open(template_filename, 'w', encoding='utf-8') as f:
                json.dump(current_state[template['name']], f, ensure_ascii=False, indent=4)

    # Read desired state files
    if args['desired_state_dir'] == '':
        print('No desired_state_dir defined. Just caching current state to disk.')
        sys.exit(0)

    desired_state = {}
    logger.info('Reading desired state for comparison')
    for path in find_json_files(args['desired_state_dir']):
        # Generate required variables
        path_temp = path.replace(args['desired_state_dir'], '').strip('/')
        exploded_path = path_temp.split('/')
        template_name = exploded_path[-1].strip('.json')

        # Read files in
        with open(path) as f:
            json_data = json.load(f)
            desired_state[template_name] = json_data

    # Compare states
    logger.info('Comparing states')
    for template in current_state:
        print(f'Template: {template}')
        if template in desired_state:
            print(DeepDiff(current_state[template], desired_state[template]))
        else:
            print(f'{template} not found in desired state.')


if __name__ == '__main__':
    logger = mylogger.init(MODULE, f'{DIR_VAR}/log/{MODULE}.log')
    logger.info('Starting zct')

    # Initialise arguments and call main
    args = parse_args()
    main(args)
