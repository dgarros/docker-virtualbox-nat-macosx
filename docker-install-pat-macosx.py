from docker import Client
import docker.tls as tls
from os import path
import pprint
import subprocess
import sys,getopt,argparse,os.path, math

parser = argparse.ArgumentParser(description='./docker-install-pat-macosx.py -c container-name -a add/delete')
parser.add_argument('-c','--container', help='Docker container name', required=True)
parser.add_argument('-a','--action', help='add or delete', required=True)
args = parser.parse_args()

try:
    args.container
except ContainerNameNotDefined:
    print "./docker-install-pat-macosx.py -c container-name must be defined"

try:
    args.action
except ActionNotDefined:
    print "./docker-install-pat-macosx.py -a add/delete must be defined"

dockerout = subprocess.check_output(
    ['/usr/local/bin/docker-machine ip default'],
    shell=True, stderr=subprocess.STDOUT
)

dockerip = dockerout.splitlines()[0]

CERTS = path.join(path.expanduser('~'), '.docker', 'machine', 'machines', 'default')

tls_config = tls.TLSConfig(
    client_cert=(path.join(CERTS, 'cert.pem'), path.join(CERTS,'key.pem')),
    ca_cert=path.join(CERTS, 'ca.pem'),
    assert_hostname=False,
    verify=True
)

url = "https://" + dockerip + ":2376"
print "URL: " + url
c = Client(base_url= url, tls=tls_config)

ports = c.inspect_container(args.container)['NetworkSettings']['Ports']

for portinfo, portdetails in ports.iteritems():
    if ports[portinfo] is not None:
        [internal_port, proto] = portinfo.split("/")

        # Catch external port instead of internal
        external_port =''
        if ports[portinfo][0]['HostPort'] is not None:
            external_port = ports[portinfo][0]['HostPort']
        else:
            external_port = internal_port

        rulename = proto + "-port" + external_port

        if args.action == 'add':
            natrule = rulename + "," + proto + ",," + external_port + ",," + external_port
            natcmd = 'VBoxManage controlvm "default" natpf1 ' + '""' + natrule + '""'
            print "NATRULE: " + natrule
            subprocess.call(natcmd, shell=True)
        elif args.action == 'delete':
            natcmd = 'VBoxManage controlvm "default" natpf1 delete ' + rulename
            subprocess.call(natcmd, shell=True)
