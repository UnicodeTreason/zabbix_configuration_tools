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
        parser.add_argument('arg1', type=str, help='First Argument')
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
    print('Connected to Zabbix API Version %s' % zapi.api_version())

    # Get all host groups
    for hostgroup in zapi.hostgroup.get():
        # Skip groups not defined as root group or a child of the root group
        if app_config['zabbix']['root_group'] not in hostgroup["name"]:
            continue

        # Get templates in desired groups
        for template in zapi.template.get(groupids=hostgroup["groupid"]):
            print(f'{template["name"]} ({template["templateid"]})')

            # Get template configuration
            api_params = {'templates': [template["templateid"]]}
            result = zapi.configuration.export(format='json', options=api_params)
            template_current = json.loads(result)

            print(f'Caching {template["name"]} to disk')
            with open(f'{DIR_VAR}/cache/{template["name"]}.json', 'w', encoding='utf-8') as f:
                json.dump(template_current, f, ensure_ascii=False, indent=4)

    # # Get git copy
    # with open('tem.json') as json_file:
    #     template_truth = json.load(json_file)

    # print(f'NameCurr: {template_current["zabbix_export"]["date"]}')
    # print(f'NameTruth: {template_truth["zabbix_export"]["date"]}')

    # diff = DeepDiff(template_current, template_truth)
    # print(diff)


if __name__ == '__main__':
    logger = mylogger.init(MODULE, f'{DIR_VAR}/log/{MODULE}.log')
    logger.info('Starting zct')

    # Initialise arguments and call main
    args = parse_args()
    main(args)
