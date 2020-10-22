import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

from ckan.logic import auth_allow_anonymous_access
from ckan.model.package_relationship import PackageRelationship
from ckanext.relationships import blueprint, constants, helpers, overrides
from ckanext.relationships.logic.auth import create as auth_create
from ckanext.relationships.logic.auth import get as auth_get
from ckanext.relationships.logic.action import create as actions_create, delete as actions_delete, get as actions_get
from ckan.model.package import Package

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
            'get_subject_package_relationship_objects': helpers.get_subject_package_relationship_objects,
            'show_relationships_on_dataset_detail': helpers.show_relationships_on_dataset_detail,
        }

    # IBlueprint

    def get_blueprint(self):
        return blueprint.relationships

    # IConfigurable

    def configure(self, config):
        PackageRelationship.types = constants.RELATIONSHIP_TYPES
        PackageRelationship.as_dict = overrides.package_relationship_as_dict
        Package.get = overrides.package_get

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
