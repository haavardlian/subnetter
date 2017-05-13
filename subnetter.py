#!/usr/bin/env python

import argparse
import ipaddress
import json
import math

from jsonschema import validate
from jsonschema.exceptions import ValidationError

from os import makedirs, path

from sys import exit, stderr

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

JSON_SCHEMA = {
    "items": {
        "properties": {
            "network": {
                "type": "string"
            },
            "subnets": {
                "items": {
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "number": {
                            "type": "integer"
                        },
                        "per-row": {
                            "type": "integer"
                        },
                        "size": {
                            "type": "integer"
                        }
                    },
                    "required": [
                        "name",
                        "size"
                    ],
                    "type": "object"
                },
                "type": "array"
            }
        },
        "required": [
            "subnets",
            "network"
        ],
        "type": "object"
    },
    "type": "array"
}


class Subnet:
    network = None

    def __init__(self, size, name):
        self.size = size
        self.name = name

    def matches(self, size):
        return self.network is None and self.size == size

    def __lt__(self, other):
        return self.network.compare_networks(other.network) == -1


def split_network(networks):
    return sum([list(net.subnets()) for net in networks], [])


def merge_networks(networks):
    return list(ipaddress.collapse_addresses(networks))


def create_config_from_template(template_path, attr):
    folder, file = path.split(template_path)
    env = Environment()
    env.loader = FileSystemLoader(folder)
    config = env.get_template(file)

    return config.render(attr)


def get_network_attributes(subnet, port):
    addresses = [str(ip) for ip in subnet.network]
    return {
        'port': port,
        'name': subnet.name,
        'prefix': str(subnet.network),
        'network': addresses[0],
        'gateway': addresses[1],
        'broadcast': addresses[-1],
        'start': addresses[2],
        'addresses': addresses[1:-1],
        'end': addresses[-2],
        'netmask': subnet.network.netmask,
        'size': subnet.network.prefixlen,
    }


def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)


def main():
    parser = argparse.ArgumentParser(description='Divides networks based on JSON description'
                                                 ' and generates config files based on jinja2 templates.')
    parser.add_argument('-n', '--network', dest='network_file', action='store', required=True,
                        help='File containing network description in JSON format')
    parser.add_argument('-t', '--template', dest='template', action='store', help='jinja2 template', required=True)
    parser.add_argument('-f', '--file', dest='file', action='store_true', default=False,
                        help='Output each resulting network to a file')
    parser.add_argument('-o', '--output-dir', dest='out_dir', action='store', default='./output', required=False,
                        help='Folder to store files in')

    args = parser.parse_args()

    try:
        with open(args.network_file) as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        print('{} was not found'.format(args.network_file), file=stderr)
        return 1

    if not path.exists(args.template):
        print('{} was not found'.format(args.template), file=stderr)
        return 1

    try:
        validate(json_data, JSON_SCHEMA)
    except ValidationError as e:
        print('{} is not valid. {}'.format(args.network_file, e.message), file=stderr)
        return 1

    for part in json_data:
        try:
            network = ipaddress.ip_network(part['network'])
        except ValueError as e:
            print(e, file=stderr)
            return 1
        total = 0
        largest_network = network.max_prefixlen
        subnets = []
        # Create all subnets
        for subnet in part['subnets']:
            if 'per-row' not in subnet:
                subnet['per-row'] = 1
            if 'number' not in subnet:
                subnet['number'] = 1
            if subnet['number'] == 0:
                continue
            if subnet['size'] < largest_network:
                largest_network = subnet['size']
            if subnet['size'] > network.max_prefixlen:
                print('Cannot create a /{} network from {}'.format(subnet['size'], network), file=stderr)
                return 1

            total += int(math.pow(2, network.max_prefixlen - subnet['size']) * subnet['number'] * subnet['per-row'])

            if subnet['number'] > 1:
                for i in range(1, subnet['number'] + 1):
                    if subnet['per-row'] > 1:
                        for j in range(1, subnet['per-row'] + 1):
                            subnets.append(Subnet(subnet['size'], '{}-{}-{}'.format(subnet['name'], i, j)))
                    else:
                        subnets.append(Subnet(subnet['size'], '{}-{}'.format(subnet['name'], i)))
            else:
                subnets.append(Subnet(subnet['size'], subnet['name']))

        # Check if we have enough addresses
        if total > network.num_addresses:
            print('Can\'t fit subnets into network :(. Tried to fit {} addresses into {} ({} addresses).'
                  .format(total, network, network.num_addresses), file=stderr)
            return 1

        # Assign networks
        networks = list(network.subnets(new_prefix=largest_network))
        while any(subnet.network is None for subnet in subnets):
            current_size = networks[0].prefixlen if networks else 0
            for subnet in [s for s in subnets if s.matches(current_size)]:
                subnet.network = networks.pop(0)
            networks = split_network(networks)

        # Render templates and write to stdout or file
        for i, net in enumerate(sorted(subnets), 1):
            attributes = get_network_attributes(net, i)
            rendered = create_config_from_template(args.template, attributes)
            if args.file:
                if not path.exists(args.out_dir):
                    makedirs(args.out_dir)
                write_to_file(path.join(args.out_dir, attributes['name']), rendered)
            else:
                print(rendered)

        # Print info about remaining networks
        if networks:
            merged = [str(net) for net in merge_networks(networks)]
            plural = 'networks' if len(merged) > 1 else 'network'
            print('Remaining {}: {}'.format(plural, ', '.join(merged)), file=stderr)
    return 0


if __name__ == '__main__':
    exit(main())
