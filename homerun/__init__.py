import subprocess
import re

def spawn(*args):
    try:
        return subprocess.check_output(args)
    except subprocess.CalledProcessError:
        return None
    
def hdhomerun_config(*args):
    return spawn('hdhomerun_config', *args)

def check():
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
    return hdhomerun_config(device, 'get', option)

def set_value(device, option, value):
    return hdhomerun_config(device, 'set', option, value)
    
def scan(device, tuner):
    args = ['hdhomerun_config', device, 'scan', tuner]
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    lines = (i.strip() for i in p.stdout)

    channel = None
    for line in lines:

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
