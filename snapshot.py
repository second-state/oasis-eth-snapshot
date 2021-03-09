import os
import json
import time
from datetime import datetime

def dump_list(cur_time, cur_folder, ty):
    cmd = './oasis-node registry '+ty+' list -v -a unix:./node/internal.sock'
    stream = os.popen(cmd)
    tylist = stream.read()
    tyfn = './'+ty+'_list.'+cur_time+'.json'
    with open(os.path.join(cur_folder, tyfn), 'w') as f:
        f.write(tylist);
    return tyfn

def dump_entity_list(cur_time, cur_folder):
    return os.path.join(cur_folder, dump_list(cur_time, cur_folder, 'entity'))

def dump_runtime_list(cur_time, cur_folder):
    return dump_list(cur_time, cur_folder, 'runtime')

def dump_node_list(cur_time, cur_folder):
    return dump_list(cur_time, cur_folder, 'node')

def dump_stake_list(cur_time, cur_folder):
    cmd = './oasis-node stake list -v -a unix:./node/internal.sock'
    stream = os.popen(cmd)
    tylist = stream.read()
    tyfn = './stake_list.'+cur_time+'.json'
    with open(os.path.join(cur_folder, tyfn), 'w') as f:
        f.write(tylist);
    return tyfn

def retrieve_entities(entity_list_name):
    entities = []
    with open(entity_list_name, 'r') as f:
        lines = f.readlines()
        for line in lines:
            entity = json.loads(line)
            entities.append(entity['id'])
    return entities

def dump_entity_account_info(entity, cur_time, accounts_folder):
    cmd = './oasis-node stake pubkey2address --public_key '+entity
    stream = os.popen(cmd)
    address = stream.read().strip()
    fn = './account_info.'+address+'.'+cur_time+'.txt'
    with open(os.path.join(accounts_folder, fn), 'w') as f:
        f.write(entity)
        f.write('\n')
        f.write(address)
        f.write('\n')
        cmd = './oasis-node stake account info -a unix:./node/internal.sock --stake.account.address '+address
        stream = os.popen(cmd)
        output = stream.read()
        f.write(output)

def get_current_timestamp():
    return time.time()

def prepare_folder(cur_time):
    '''
    /home/user/mainnet/ <- cwd
    /home/user/mainnet/dump_state/ <- the root of dumping the state
    /home/user/mainnet/dump_state/timestamp/ <- state of timestamp
        |- entity_list.json
        |- runtime_list.json
        |- node_list.json
        |- stake_list.json
        |- accounts_info <DIR>
    /home/user/mainnet/dump_state/timestamp/accounts_info/ <- stake amount of every entity
        |- account_info.<address>.txt
    '''
    cwd = os.getcwd()
    root_path = os.path.join(cwd, 'dump_state')
    cur_folder = os.path.join(root_path, cur_time)
    accounts_folder = os.path.join(cur_folder, 'accounts_info')

    try:
        os.makedirs(cur_folder)
        os.makedirs(accounts_folder)
    except OSError:
        print ("Creation of the directory failed")
    else:
        print ("Successfully created the directory")

    return cur_folder, accounts_folder

def main():
    # Get current time
    cur_time = str(get_current_timestamp())
    print('Current time: ', cur_time)
    print(datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))
    cur_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    # Check file structure
    cur_folder, accounts_folder = prepare_folder(cur_time)
    # Dump entity list
    print('Dump entity list...')
    entity_list_name = dump_entity_list(cur_time, cur_folder)
    print('Dump entity list... done')
    # Dump runtime list
    print('Dump runtime list...')
    runtime_list_name = dump_runtime_list(cur_time, cur_folder)
    print('Dump runtime list... done')
    # Dump node list
    print('Dump node list...')
    node_list_name = dump_node_list(cur_time, cur_folder)
    print('Dump node list... done')
    # Dump stake list
    print('Dump stake list...')
    stake_list_name = dump_stake_list(cur_time, cur_folder)
    print('Dump stake list... done')
    # Retrieve account address from entity list
    print('Retrieve entities...')
    entities = retrieve_entities(entity_list_name)
    print('Retrieve entities... done')
    # Query account info from the previous account address
    print('Query all account info...')
    for entity in entities:
        print('     Handle entity: ', entity)
        dump_entity_account_info(entity, cur_time, accounts_folder)
        print('     Handle entity: ', entity, '... done')
    print('Query all account info... done')


if __name__ == '__main__':
    main()

