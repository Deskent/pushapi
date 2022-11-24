#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Примеры использования pushAPI - главный модуль.'''

import argparse
import userdemo


HOST_DFL = "10.78.216.60"
PORT_DFL = 9101
NAME_DFL = "eXpress"

def parse_args():
    '''Разбор параметров командной строки/'''
    parser = argparse.ArgumentParser(description="python PushAPI demo")

    parser.add_argument("--host", action="store", type=str, default=HOST_DFL,
                        help="PushAPI server hostname (default: %s)" % HOST_DFL)
    parser.add_argument("--port", action="store", type=int, default=PORT_DFL,
                        help="PushAPI server port (default: %d)" % PORT_DFL)
    parser.add_argument("--id", action="store", type=str, default=NAME_DFL,
                        metavar="NAME", dest="name",
                        help="company identificator (default: %s)" % NAME_DFL)
    parser.add_argument("--token", action="store", type=str, required=True,
                        help="company's authentication token")

    return parser.parse_args()


def main():
    '''Утилита командной строки запуска примеров pushAPI - точка входа.'''
    # args = parse_args()
    # TOKEN_DFL = "vvrn3oczp08q1fx34l9y"
    HOST_DFL = "10.78.216.60"
    PORT_DFL = 9101
    NAME_DFL = "briz"
    # TOKEN_DFL = "vvrn3oczp08q1fx34l9y"
    TOKEN_DFL = "nqbu3qyecyvoge7swsuu"

    # args.token = TOKEN_DFL
    # demo = userdemo.UserDemo(args.host, args.port, args.name, TOKEN_DFL)
    demo = userdemo.UserDemo(HOST_DFL, PORT_DFL, NAME_DFL, TOKEN_DFL)
    demo.run()


if __name__ == '__main__':
    main()