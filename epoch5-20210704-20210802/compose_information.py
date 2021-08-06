#!/usr/bin/env python3

import json
import os
import subprocess

"""
The output format will be:
    GitHub_Entity_Filename,Oasis_Entity_ID,Oasis_Account,ETH_Address,Stake_Amount_Day1,Stake_Amount_Day2,...Stake_Amount_Day30
    If the paratime node is dead, your stake amount will be set to zero.
"""

RUNTIME_ID = 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA/wQ='

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
            #print('Stake ... ', k, self.stake_amount[k])
            s.append(self.stake_amount[k])
        return ','.join(s)
    def __repr__(self):
        s = [self.entity_filename, self.oasis_id, self.oasis_account, self.eth_address]
        for k in self.stake_amount:
            #print('Stake ... ', k, self.stake_amount[k])
            s.append(self.stake_amount[k])
        return ','.join(s)

    def load_entity(self, line):
        p = line.split(',')
        self.entity_filename = p[0]
        self.oasis_id = p[1]
        self.oasis_account = p[2]
        self.eth_address = p[3]
    def load_stake_amount(self, date, nodes):
        p = os.path.join(date, 'accounts_info', 'account_info.'+self.oasis_account+'.'+date+'.txt')
        try:
            with open(p) as f:
                print("Handle ... ", p)
                lines = f.readlines()
                targetI = 0;
                for i in range(len(lines)):
                    if lines[i].startswith("Active Delegations to this Account:"):
                        targetI = i+1
                        break
                print(lines[targetI].split()[1].strip())
                self.stake_amount[date] = lines[targetI].split()[1].strip()
                if self.oasis_id not in nodes:
                    print("NOT in the nodes")
                    self.stake_amount[date] = '-1'
        except:
            print("ERROR")
            self.stake_amount[date] = '-2'

def load_entities():
    entities = []
    with open('./whitelisted_entities.csv') as f:
        for _,line in enumerate(f):
            e = Entity()
            e.load_entity(line)
            entities.append(e)
    return entities

def get_dates():
    return [p for p in os.listdir('.') if os.path.isdir(os.path.join('.',p))]

def main():
    dates = sorted(get_dates())
    entities = load_entities()
    print(entities)
    for date in dates:
        nodes = {}
        p = os.path.join('.', date, 'node_list.'+date+'.json')
        with open(p) as f:
            for _,line in enumerate(f):
                node = json.loads(line)
                if node['roles'] == 1:
                    print(date, "GET COMPUT NODE", node['entity_id'])
                    # Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 1
                elif node['roles'] == 35:
                    print(date, "GET GENESIS NODE", node['entity_id'])
                    # Storage + Compute node
                    if node['runtimes'][0]['id'] == RUNTIME_ID:
                        nodes[node['entity_id']] = 35
                else:
                    continue
        for e in entities:
            e.load_stake_amount(date, nodes)
    print(entities)
    with open('reward_base.csv', 'w') as f:
        b = ['GitHub_Entity_Filename,Oasis_Entity_ID,Oasis_Account,ETH_Address']
        b.extend(dates)
        f.write(','.join(b)+'\n')
        for e in entities:
            f.write(str(e)+'\n')

if __name__ == '__main__':
    main()
