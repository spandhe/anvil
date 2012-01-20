# vim: tabstop=4 shiftwidth=4 softtabstop=4

#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import Logger
import Util
import Shell

#TODO fix these
from Component import (PythonUninstallComponent,
                       PythonInstallComponent,
                       NullRuntime)

LOG = Logger.getLogger("install.horizon")
TYPE = Util.HORIZON

ROOT_HORIZON = 'horizon'
HORIZON_NAME = 'horizon'
ROOT_DASH = 'openstack-dashboard'
DASH_NAME = 'dashboard'

HORIZON_PY_CONF = "horizon_settings.py"
HORIZON_PY_CONF_TGT = ['local', 'local_settings.py']
CONFIGS = [HORIZON_PY_CONF]


class HorizonUninstaller(PythonUninstallComponent):
    def __init__(self, *args, **kargs):
        PythonUninstallComponent.__init__(self, TYPE, *args, **kargs)


class HorizonInstaller(PythonInstallComponent):
    def __init__(self, *args, **kargs):
        PythonInstallComponent.__init__(self, TYPE, *args, **kargs)
        self.git_loc = self.cfg.get("git", "horizon_repo")
        self.git_branch = self.cfg.get("git", "horizon_branch")
        self.horizon_dir = Shell.joinpths(self.appdir, ROOT_HORIZON)
        self.dash_dir = Shell.joinpths(self.appdir, ROOT_DASH)

    def _get_download_locations(self):
        places = PythonInstallComponent._get_download_locations(self)
        places.append({
            'uri': self.git_loc,
            'branch': self.git_branch,
        })
        return places

    def _get_target_config_name(self, config_name):
        if(config_name == HORIZON_PY_CONF):
            return Shell.joinpths(self.dash_dir, *HORIZON_PY_CONF_TGT)
        else:
            return PythonInstallComponent._get_target_config_name(self, config_name)

    def _get_python_directories(self):
        py_dirs = list()
        py_dirs.append({
            'name': HORIZON_NAME,
            'work_dir': self.horizon_dir,
        })
        py_dirs.append({
            'name': DASH_NAME,
            'work_dir': self.dash_dir,
        })
        return py_dirs

    def _get_config_files(self):
        #these are the config files we will be adjusting
        return list(CONFIGS)

    def _get_param_map(self, config_fn):
        #this dict will be used to fill in the configuration
        #params with actual values
        mp = dict()
        mp['OPENSTACK_HOST'] = Util.get_host_ip(self.cfg)
        return mp


class HorizonRuntime(NullRuntime):
    def __init__(self, *args, **kargs):
        NullRuntime.__init__(self, TYPE, *args, **kargs)
