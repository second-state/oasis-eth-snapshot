#!/usr/bin/env python3

import json
import os
import subprocess

"""
The output format will be:
    GitHub_Entity_Filename,Oasis_Entity_ID,Oasis_Account,ETH_Address,Stake_Amount_Day1,Stake_Amount_Day2,...Stake_Amount_Day30
    If the paratime node is dead, your stake amount will be set to zero.
"""

RUNTIME_ID = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wM='
BEFORE_COBALT_UPGRADE = 'before_cobalt_upgrade'
AFTER_COBALT_UPGRADE = 'after_cobalt_upgrade'

class Entity():
    def __init__(self):
        self.entity_filename = ""
        self.oasis_id = ""
        self.oasis_account = ""
        self.eth_address = ""
        self.stake_amount = {}
    def __str__(self):
        s = [self.entity_filename, self.oasis_id, self.oasis_account, self.eth_address]
        for k in self.stake_amount:
            print('Stake ... ', k, self.stake_amount[k])
            s.append(self.stake_amount[k])
        return ','.join(s)
    def __repr__(self):
        s = [self.entity_filename, self.oasis_id, self.oasis_account, self.eth_address]
        for k in self.stake_amount:
            print('Stake ... ', k, self.stake_amount[k])
            s.append(self.stake_amount[k])
        return ','.join(s)

    def load_entity(self, line):
        p = line.split(',')
        self.entity_filename = p[0]
        self.oasis_id = p[1]
        self.oasis_account = p[2]
        self.eth_address = p[3]
    def load_stake_amount(self, prefix, date, nodes):
        p = os.path.join(prefix, date, 'accounts_info', 'account_info.'+self.oasis_account+'.'+date+'.txt')
        try:
            with open(p) as f:
                print("Handle ... ", p)
                lines = f.readlines()
                if prefix == BEFORE_COBALT_UPGRADE:
                    print(lines[7].split()[2].strip())
                    self.stake_amount[date] = lines[7].split()[2].strip()
                else:
                    targetI = 0;
                    for i in range(len(lines)):
                        if lines[i].startswith("Active Delegations to this Account:"):
                            targetI = i+1
                            break
                    print(lines[targetI].split()[1].strip())
                if self.oasis_id not in nodes:
                    self.stake_amount[date] = '-1'
        except:
            self.stake_amount[date] = '-2'

def load_entities():
    entities = []
    with open('./whitelisted_entities.csv') as f:
        for _,line in enumerate(f):
            e = Entity()
            e.load_entity(line)
            entities.append(e)
    return entities

def get_dates(cobalt_upgrade):
    if cobalt_upgrade == True:
        return [p for p in os.listdir(AFTER_COBALT_UPGRADE) if os.path.isdir(os.path.join(AFTER_COBALT_UPGRADE,p))]
    else:
        return [p for p in os.listdir(BEFORE_COBALT_UPGRADE) if os.path.isdir(os.path.join(BEFORE_COBALT_UPGRADE,p))]

def main():
    before_cobalt_upgrade = sorted(get_dates(False))
    after_cobalt_upgrade = sorted(get_dates(True))
    entities = load_entities()
    print(entities)
    for date in before_cobalt_upgrade:
        nodes = {}
        p = os.path.join(BEFORE_COBALT_UPGRADE, date, 'node_list.'+date+'.json')
        with open(p) as f:
            for _,line in enumerate(f):
                node = json.loads(line)
                if node['roles'] == 1:
                    # Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 1
                elif node['roles'] == 3:
                    # Storage + Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 3
                else:
                    continue
        for e in entities:
            e.load_stake_amount(BEFORE_COBALT_UPGRADE, date, nodes)
    for date in after_cobalt_upgrade:
        nodes = {}
        p = os.path.join(AFTER_COBALT_UPGRADE, date, 'node_list.'+date+'.json')
        with open(p) as f:
            for _,line in enumerate(f):
                node = json.loads(line)
                if node['roles'] == 1:
                    # Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 1
                elif node['roles'] == 3:
                    # Storage + Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 3
                else:
                    continue
        for e in entities:
            e.load_stake_amount(AFTER_COBALT_UPGRADE, date, nodes)
    print(entities)
    with open('reward_base.csv', 'w') as f:
        b = ['GitHub_Entity_Filename,Oasis_Entity_ID,Oasis_Account,ETH_Address']
        b.extend(before_cobalt_upgrade)
        b.extend(after_cobalt_upgrade)
        f.write(','.join(b)+'\n')
        for e in entities:
            f.write(str(e)+'\n')

if __name__ == '__main__':
    main()
