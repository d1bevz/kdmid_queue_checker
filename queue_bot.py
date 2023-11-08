# -*- coding: utf-8 -*-

import time
import os
import argparse 

from queue_class import QueueChecker

# kdmid_subdomain = 'madrid' 
# order_id = '123610' 
# code = '7AE8EFCC' 
# every_hours = 3

def run(queue_checker, every_hours): 
    anyPending = True
    while anyPending:
        anyPending = False
        for order_id, code in queue_checker.order_code_pairs:
            if not os.path.isfile(f"{order_id}_{code}_success.txt"): 
                anyPending = True
                queue_checker.check_queue()
                time.sleep(every_hours*3600)
            else: 
                print(f'Appointment found for order {order_id}, exiting')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parameters for checking the queue')
    parser.add_argument('--subdomain', type=str, required=True, help='The city where the consulate is situated')
    parser.add_argument('--order_code_pairs', type=str, nargs='+', help='Pairs of order_id and code')
    parser.add_argument('--every_hours', type=int, default=2, help='Every n hours to check the queue, default 2')
    
    args = parser.parse_args()
    
    # Parse order_code_pairs argument into a list of tuples
    order_code_pairs = []
    for pair in args.order_code_pairs:
        order_id, code = pair.split(',')
        order_code_pairs.append((order_id, code))
    
    queue_checker = QueueChecker(args.subdomain, order_code_pairs)
    run(queue_checker, args.every_hours)
