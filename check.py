#!/usr/bin/env python3

import json
import os
import subprocess

RUNTIME_ID = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wM='
TARGET_DATETIME = '2021-03-08-05-00-02'

def find_json_by_entity_id(entity_id):
    command = f'grep -rl {entity_id} ../oasis-ssvm-paratime-entities/mainnet'
    json_file = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    return json_file

def check_validator_by_entity_id(entity_id):
    command = f'grep -rl "{entity_id}" {TARGET_DATETIME}/accounts_info'
    account_info_file = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    command = f'grep "Global: node-validator" {account_info_file}'
    returncode = subprocess.run(command, shell=True, capture_output=True).returncode
    if returncode == 0:
        return True
    return False

def get_paratime_entities():
    command = 'cat ../oasis-ssvm-paratime-entities/mainnet/*.json | jq -r .OasisEntityID'
    output = subprocess.check_output(command, shell=True).decode('utf-8').strip()
    return output.split('\n')

def main():
    whitelist = get_paratime_entities()

    with open(f'{TARGET_DATETIME}/node_list.{TARGET_DATETIME}.json') as f:
        nodelist = f.readlines()
        nodelist = list(map(json.loads, nodelist))

    entity_running_ssvm = []
    for node in nodelist:
        node_id = node['id']
        entity_id = node['entity_id']
        if node['runtimes'] is not None:
            has_ssvm_runtime = False
            for runtime in node['runtimes']:
                if runtime['id'] == RUNTIME_ID:
                    has_ssvm_runtime = True
                    break
            if has_ssvm_runtime:
                if entity_id not in entity_running_ssvm:
                    entity_running_ssvm.append(entity_id)

    entity_without_running_ssvm = whitelist.copy()
    for entity in entity_running_ssvm:
        if entity in entity_without_running_ssvm:
            entity_without_running_ssvm.remove(entity)

    print(f'Run SSVM ({len(entity_running_ssvm)})')
    for entity in entity_running_ssvm:
        filename = find_json_by_entity_id(entity).split('/')[-1]
        print(f'{entity} / {check_validator_by_entity_id(entity)} / {filename}')
    print()
    print(f'No Run SSVM ({len(entity_without_running_ssvm)})')
    for entity in entity_without_running_ssvm:
        filename = find_json_by_entity_id(entity).split('/')[-1]
        print(f'{entity} / {filename}')

if __name__ == '__main__':
    main()

