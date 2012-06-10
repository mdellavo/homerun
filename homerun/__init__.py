import subprocess
import re

def spawn(*args):
    try:
        return subprocess.check_output(args)
    except subprocess.CalledProcessError:
        return None

# FIXME need a better name
def spawn_lines(*args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    output = (i.strip() for i in p.stdout)
    return (i for i in output if i)

def hdhomerun_config(*args):
    return spawn('hdhomerun_config', *args)

def hdhomerun_config_lines(*args):
    return spawn_lines('hdhomerun_config', *args)

def kv_to_dict(s):
    return dict(i.split('=') for i in s.split())

def kvlist_to_dict(lines):
    kv_lines = (line.split(':') for line in lines)
    return dict((k, v.split()) for k,v in kv_lines)

def check_hdhomerun_config():
    return bool(spawn('which', 'hdhomerun_config'))

def discover():
    out = hdhomerun_config('discover')
    if not out:
        return None

    match = re.match(r'hdhomerun device (\w+) found at ([\d\.]+)', out.strip())
    if not match:
        return None

    return {
        'id': match.group(1), 
        'ip': match.group(2)
    }

def get_value(device, option):
    value = hdhomerun_config(device, 'get', option)
    return value.strip() if value else None

def get_value_lines(device, option):
    return hdhomerun_config_lines(device, 'get', option)

def get_value_dict(device, option):
    value = get_value(device, option)
    return kv_to_dict(value) if value else None

def get_value_dictlist(device, option):
    value = get_value_lines(device, option)
    return kvlist_to_dict(value) if value else None

def set_value(device, option, value):
    return hdhomerun_config(device, 'set', option, value)
    
def scan(device, tuner):
    channel = None
    for line in hdhomerun_config_lines(device, 'scan', tuner):

        match = re.match(r'SCANNING: (\d+)', line)
        if match:
            channel = match.group(1)
            continue

        match = re.match(r'PROGRAM (\d+): (\d+) (.*)', line)
        if match:

            name = match.group(3)
            if name.endswith(' (encrypted)'):
                name = name[:-len(' (encrypted)')]

            yield {
                'channel': channel,
                'program': match.group(1),
                'number': match.group(2),
                'name': name
            }

def num_tuners(device):
    i = 0

    while True:
        if not get_value(device, '/tuner%d/status' % i):
            break

        i += 1

    return i

def get_tuner_names(device):
    for i in range(num_tuners(device)):
        yield 'tuner' % i

def get_device_model(device):
    return get_value(device, '/sys/model')

def get_device_hwmodel(device):
    return get_value(device, '/sys/hwmodel')

def get_device_features(device):
    return get_value_dictlist(device, '/sys/features')

def get_device_version(device):
    return get_value(device, '/sys/version')

def get_card_status(device):
    return get_value_dict(device, '/card/status')

def get_tuner_status(device, tuner):
    return get_value_dict(device, '/tuner%d/status' % tuner)
