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
import pdb

from oslo_log import log as logging

from solumclient import client as solum_client
from solumclient.openstack.common.apiclient import exceptions

from heat.engine.clients import client_plugin

CLIENT_NAME = 'solum'


LOG = logging.getLogger(__name__)

class SolumClientPlugin(client_plugin.ClientPlugin):

    exceptions_module = exceptions

    service_types = [APPLICATION_DEPLOYMENT] = ['application_deployment']

    def _create(self, version=None):
        con = self.context
        endpoint_type = self._get_client_option(CLIENT_NAME, 'endpoint_type')
        endpoint = self.url_for(service_type=self.APPLICATION_DEPLOYMENT,
                                endpoint_type=endpoint_type)
        args = {
            'endpoint': endpoint,
            'token': con.auth_token,
            'auth_url': con.auth_url,
            'tenant_name': 'demo',
        }
        pdb.set_trace()
        return solum_client.Client(version if version else '1', **args)

    def is_client_exception(self, ex):
        return isinstance(ex, exceptions.ClientException)

    def is_not_found(self, ex):
        return (isinstance(ex, exceptions.ClientException) and
                ex.http_status == 404)

    def is_over_limit(self, ex):
        return (isinstance(ex, exceptions.ClientException) and
                ex.http_status == 413)

    def is_conflict(self, ex):
        return (isinstance(ex, exceptions.ClientException) and
                ex.http_status == 409)



