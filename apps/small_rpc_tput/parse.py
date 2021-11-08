#!/usr/bin/env python3
import json
import re
from argparse import ArgumentParser
from collections import defaultdict
from statistics import mean


def main(args):
    pattern = re.compile(r'thread (\d+): (\d+(\.\d+)?) Mrps')

    mrps_dict = defaultdict(list)

    with open(args.input) as f:
        lines = f.read().splitlines()

    for l in lines:
        m = pattern.search(l)
        if m is None:
            continue
        t, mrps = int(m.group(1)), float(m.group(2))
        mrps_dict[t].append(mrps)

    mrps_dict = {t: mean(sorted(mrps_list)[2:-2]) for t, mrps_list in mrps_dict.items()}
    for t, mrps in mrps_dict.items():
        print("thread {:02d}, Mrps = {:.3f}".format(t, mrps))

    total_mrps = sum(mrps_dict.values())
    print("Total Mrps: {:.3f}".format(total_mrps))

    if args.output is not None:
        params = {}
        with open('apps/small_rpc_tput/config') as f:
            print('Reading app config')
            lines = f.read().splitlines()
            for l in lines:
                if not l.startswith('--'):
                    continue

                param_name, param_value = l[2:].split(' ')
                params[param_name] = param_value

        hosts = []
        with open('scripts/autorun_process_file') as f:
            print('Reading process file')
            lines = f.read().splitlines()
            hosts = [l.split(' ')[0] for l in lines]

        data = {'app_params': params, 'thread_mrps': mrps_dict, 'total_mrps': total_mrps, 'hosts': hosts}
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2)


if __name__ == '__main__':
    parser = ArgumentParser(
        description='Parse per-thread and total performance from small_rpc_tput\'s standard output.')
    parser.add_argument('input', help='Path to the stdout log file')
    parser.add_argument('-o', '--output', help='Path to save record')
    args = parser.parse_args()
    main(args)
