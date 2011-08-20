from fabric.api import *
from datetime import datetime
env.hosts = ['coclass.com']

def deploy():
    remote_app_repo_dir='/home/clay/dev/CoClass/'
    remote_app_srv_dir='/srv/http/CoClass/'
    dtn = datetime.now().isoformat()
    sudo('mv %s /tmp/CoClass-%s' % (remote_app_srv_dir, str(dtn)))
    sudo('cp -r %s %s' % (remote_app_repo_dir, remote_app_srv_dir))
    sudo('apacectl restart')
    
    

