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
    return (i.strip() for i in p.stdout)

def hdhomerun_config(*args):
    return spawn('hdhomerun_config', *args)

def hdhomerun_config_lines(*args):
    return spawn_lines('hdhomerun_config', *args)

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
    rv = hdhomerun_config(device, 'get', option)
    return rv.strip() if rv else rv

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
                'vct': match.group(2),
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
    return get_value('/sys/model')

def get_device_hwmodel(device):
    return get_value('/sys/hwmodel')

def get_device_features(device):
    features = hdhomerun_config_lines(device, 'get', '/sys/features')

    if not features:
        return None

    rv = {}
    for line in features:
        if line:
            key, rest = line.split(':')
            rv[key] = rest.split()
    return rv

def get_device_version(device):
    return get_value('/sys/version')

def get_card_status(device):
    status = get_value(device, '/card/status')

    if not status:
        return None

    return dict(i.split('=') for i in status.split())
