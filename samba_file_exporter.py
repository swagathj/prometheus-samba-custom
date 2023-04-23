'''
Prometheus Samba custom Metrics
'''
from typing import Optional, List
import re
import os
import time
import subprocess
from pydantic import BaseModel


METRICS_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

path = os.path.join(METRICS_ROOT + '/file')
if not os.path.exists(path):
    os.makedirs(path)
file_path = os.path.join(path + '/samba_metrics.prom')


class SmbMetric(BaseModel):
    '''
    Pydantic Model for smb metics
    '''
    name: str
    value: float
    docker_cifs: Optional[str] = None


def collect_metrics() -> None:
    """
    Collects metrics by running the smbstatus command and extracting metrics from its output.
    """
    # Run /tmw-nas-3p/samba/bin/smbstatus -P command and capture output
    try:
        docker_output = subprocess.check_output(
            "docker ps | awk '{print $NF}' | grep cifs", \
                stderr=subprocess.STDOUT, shell=True, encoding='utf-8'
        )
    except subprocess.CalledProcessError:
        docker_output = ''

    # Run hostname | cut -f1 -d. command and capture output
    try:
        host_name_output = subprocess.check_output('hostname | cut -f1 -d.', \
            shell=True, encoding='utf-8')
    except subprocess.CalledProcessError:
        host_name_output = ''

    with open(file_path, 'w') as find:
        if docker_output:
            for i in docker_output.split('\n'):
                if i:
                    docker_cifs = i.split()[0]
                    output = subprocess.check_output(
                        [
                            'docker', 'exec', '-t', docker_cifs, \
                                '/tmw-nas-3p/samba/bin/smbstatus', '-P'
                        ]
                    )
                    smb_metrics = extract_metrics(output.decode('utf-8'))
                    for smb_metric in smb_metrics:
                        find.write(f'{smb_metric.name}{{docker_cifs="{docker_cifs}"}} \
                            {smb_metric.value}\n')
        else:
            if host_name_output:
                output = subprocess.check_output(['/tmw-nas-3p/samba/bin/smbstatus', \
                    '-P'], encoding='utf-8')
                smb_metrics = extract_metrics(output)
                for smb_metric in smb_metrics:
                    find.write(f'{smb_metric.name}{{host_name="{host_name_output.strip()}", \
                        metrics="{smb_metric.name}"}} {smb_metric.value}\n')


def extract_metrics(output: str) -> List[SmbMetric]:
    """
    Extracts metrics from smbstatus command output
    """
    smb_metrics = []
    pattern = re.compile(r'^([a-zA-Z0-9_]+):\s+([0-9]+)$')
    for line in output.splitlines():
        match = pattern.match(line.strip())
        if match:
            smb_metric = SmbMetric(name=match.group(1), value=float(match.group(2)))
            smb_metrics.append(smb_metric)
    return smb_metrics


if __name__ == '__main__':
    """
    Collects metrics every 5 seconds.
    """
    while True:
        collect_metrics()
        time.sleep(5)
