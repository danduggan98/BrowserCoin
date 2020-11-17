import sys

def get_port(args, default_port):
    num_args = len(args)
    PORT = None

    if num_args == 1:
        #No port specified - default to 5000
        PORT = default_port
    elif num_args == 2:
        #One specified - use that
        PORT = args[1]
    else:
        #Many args = running from gunicorn - use the one specified
        port_arg = args[2]
        port_idx = port_arg.find(':') + 1
        PORT = port_arg[port_idx :]
    return PORT
    