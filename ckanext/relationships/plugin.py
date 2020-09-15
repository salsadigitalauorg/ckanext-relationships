import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

from ckan.logic import auth_allow_anonymous_access
from ckan.model.package_relationship import PackageRelationship
from ckanext.relationships import blueprint, constants, helpers
from ckanext.relationships.logic.auth import create as auth_create
from ckanext.relationships.logic.auth import get as auth_get
from ckanext.relationships.logic.action import create as actions_create, delete as actions_delete, get as actions_get
from ckan.model.package import Package
from ckan.model import meta

log = logging.getLogger(__name__)


class RelationshipsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable, inherit=True)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_relationships': helpers.get_relationships,
            'get_relatable_datasets': helpers.get_relatable_datasets,
            'get_lineage_notes': helpers.get_lineage_notes,
            'get_relationship_types': helpers.get_relationship_types,
            'quote_uri': helpers.quote_uri,
        }

    # IBlueprint

    def get_blueprint(self):
        return blueprint.relationships

    # IConfigurable

    def configure(self, config):
        PackageRelationship.types = constants.RELATIONSHIP_TYPES
        Package.get = self.qdes_override_package_get

    def qdes_override_package_get(self, reference, for_update=False):
        '''Returns a package object referenced by its id or name.'''

        if not reference:
            # Find the callers method name
            # If it is from 'index_package' return a new initialised package object to prevent a error of trying to retrieve the name attribute from a None object
            # qdes_ckan-29_lagoon/ckan/ckan_core/ckan/lib/search/index.py Line 224 rel_dict[type].append(model.Package.get(rel['object_package_id']).name)
            import inspect
            calling_method = ''
            try:
                # TODO: Need to investigate potentially a better way of finding key names instead of using indexes
                calling_method = inspect.stack()[1][3]
            except Exception as e:
                log.error('qdes_override_package_get - inspect.stack: {0}'.format(e))

            if calling_method == 'index_package':
                return Package()
            else:
                return None

        q = meta.Session.query(Package)
        if for_update:
            q = q.with_for_update()
        pkg = q.get(reference)
        if pkg == None:
            pkg = Package.by_name(reference, for_update=for_update)
        return pkg

    # IActions
    def get_actions(self):
        return {
            'package_relationship_create': actions_create.package_relationship_create,
            'package_relationships_list': actions_get.package_relationships_list,
            'package_relationship_delete_by_uri': actions_delete.package_relationship_delete_by_uri,
            'package_relationship_delete_all': actions_delete.package_relationship_delete_all,
            'subject_package_relationship_objects': actions_get.subject_package_relationship_objects,
            'get_package_relationship_by_uri': actions_get.package_relationship_by_uri,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'package_relationship_create': auth_create.package_relationship_create,
            'package_relationships_list': auth_get.package_relationships_list,
        }
