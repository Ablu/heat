import pdb

import time
from oslo_log import log as logging
from solumclient.v1.workflow import WorkflowManager

from heat.common import exception
from heat.common.i18n import _
from heat.engine import resource
from heat.engine import attributes
from heat.engine import properties

LOG = logging.getLogger(__name__)


class Build(resource.Resource):
    """A resource which represents an generated image"""

    PROPERTIES = (
        APP_NAME, BUILD_TIMEOUT
    ) = (
        'app_name', 'build_timeout'
    )

    ATTRIBUTES = (
        EXTERNAL_REF
    ) = (
        'external_ref'
    )

    properties_schema = {
        APP_NAME: properties.Schema(
            properties.Schema.STRING,
            _('Name of the Solum app.')
        ),
        BUILD_TIMEOUT: properties.Schema(
            properties.Schema.INTEGER,
            _('Number of minutes to wait for a build to succeed or fail.'),
            30
        ),
    }

    attributes_schema = {
        EXTERNAL_REF: attributes.Schema(
            _('Reference to the external'),
            cache_mode=attributes.Schema.CACHE_NONE,
            type=attributes.Schema.STRING
        ),
    }

    default_client_name = 'solum'

    def init(self):
        self.attributes_schema.update(self.base_attributes_schema)

    def handle_create(self):
        app_name = self.properties[self.APP_NAME]
        build_timeout = self.properties[self.BUILD_TIMEOUT]
        app = self.client().apps.find(name_or_id=app_name)

        workflow = WorkflowManager(self.client(), app_id=app.id).create(actions=["build"])
        id_ = workflow.id

        try_until = time.time() + 60 * build_timeout
        while time.time() < try_until:
            time.sleep(5)
            workflow = WorkflowManager(self.client(), app_id=app.id).find(revision_or_id=id_)
            if workflow.status == 'BUILT':
                self.data_set(self.EXTERNAL_REF, workflow.external_ref, redact=True)
                return
            elif workflow.status == 'ERROR':
                raise exception.Error(_("Build of the Solum app %s failed") % app_name)
        raise exception.Error(_("Build of the Solum app %s timed out after %d seconds") % (app_name, build_timeout))

    def get_attribute(self, key, *path):
        if key == self.EXTERNAL_REF:
            return self.data().get(self.EXTERNAL_REF)
        return None


def resource_mapping():
    pdb.set_trace()
    return {
        'OS::Solum::Build': Build
    }
