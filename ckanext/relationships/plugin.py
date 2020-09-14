import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging

from ckan.logic import auth_allow_anonymous_access
from ckan.model.package_relationship import PackageRelationship
from ckanext.relationships import blueprint, constants, helpers
from ckanext.relationships.logic.auth import create as auth_create
from ckanext.relationships.logic.auth import get as auth_get
from ckanext.relationships.logic.action import create as actions_create, delete as actions_delete, get as actions_get, update as actions_update
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
    plugins.implements(plugins.IPackageController, inherit=True)

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
            'update_related_resources': actions_update.update_related_resources,
            'subject_package_relationship_objects': actions_get.subject_package_relationship_objects,
            'get_package_relationship_by_uri': actions_get.package_relationship_by_uri,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'package_relationship_create': auth_create.package_relationship_create,
            'package_relationships_list': auth_get.package_relationships_list,
        }

    # IPackageController

    def after_create(self, context, pkg_dict):
        u'''
        Extensions will receive the validated data dict after the dataset
        has been created (Note that the create method will return a dataset
        domain object, which may not include all fields). Also the newly
        created dataset id will be added to the dict.
        '''
        self._create_series_or_collection_relationships(context, pkg_dict)
        self._create_related_datasets_relationships(context, pkg_dict)
        self._create_related_resource_relationships(context, pkg_dict)
        self._update_related_resources(context, pkg_dict)

    def after_update(self, context, pkg_dict):
        u'''
        Extensions will receive the validated data dict after the dataset
        has been updated.
        '''
        helpers.reconcile_package_relationships(context, pkg_dict['id'], pkg_dict.get('related_resources', None))
        self._create_series_or_collection_relationships(context, pkg_dict)
        self._create_related_datasets_relationships(context, pkg_dict)
        self._create_related_resource_relationships(context, pkg_dict)
        self._update_related_resources(context, pkg_dict)

    # @TODO: Should this be moved into the ckanext-qdes-schema ?
    def _create_series_or_collection_relationships(self, context, pkg_dict):
        series_or_collection = pkg_dict.get('series_or_collection', [])
        datasets = toolkit.get_converter('json_or_string')(series_or_collection)
        relationship_type = 'isPartOf'
        self._add_related_resources(pkg_dict, datasets, relationship_type)

    # @TODO: Should this be moved into the ckanext-qdes-schema ?
    def _create_related_datasets_relationships(self, context, pkg_dict):
        related_datasets = pkg_dict.get('related_datasets', [])
        datasets = toolkit.get_converter('json_or_string')(related_datasets)
        relationship_type = 'unspecified relationship'
        self._add_related_resources(pkg_dict, datasets, relationship_type)

    # @TODO: Should this be moved into the ckanext-qdes-schema ?
    def _add_related_resources(self, pkg_dict, datasets, relationship_type):
        if not datasets or not isinstance(datasets, list):
            return
        related_resources = pkg_dict.get('related_resources', {})
        related_resources = toolkit.get_converter('json_or_string')(related_resources)
        if not related_resources:
            related_resources = {"resources": [], "relationships": [], "count": 0}

        for dataset in datasets:
            if not any(resource for resource in related_resources.get("resources", []) if resource == dataset):
                related_resources["resources"].append(dataset)
                related_resources["relationships"].append(relationship_type)
                related_resources["count"] += 1

        pkg_dict['related_resources'] = related_resources

    # @TODO: Should this be moved into the ckanext-qdes-schema ?
    def _create_related_resource_relationships(self, context, pkg_dict):
        related_resources = pkg_dict.get('related_resources', {})
        related_resources = toolkit.get_converter('json_or_string')(related_resources)
        if related_resources and isinstance(related_resources, dict):
            dataset_id = pkg_dict.get('id')
            resources = related_resources.get('resources', [])
            relationships = related_resources.get('relationships', [])

            self._create_relationships(context, dataset_id, resources, relationships)

    # @TODO: Should this be moved into the ckanext-qdes-schema ?
    def _create_relationships(self, context, dataset_id, datasets, relationships):
        try:
            for index, dataset in enumerate(datasets):
                relationship_type = relationships[index]
                relationship_dataset, relationship_url = self._get_dataset_relationship(context, dataset)

                if relationship_dataset or relationship_url:
                    relationship = toolkit.get_action('package_relationship_create')(context, {
                        'subject': dataset_id,
                        'object': relationship_dataset,
                        'type': relationship_type,
                        'comment': relationship_url,
                    })
        except Exception as e:
            log.debug('_create_relationships error: {0}'.format(e))
            raise

    def _get_dataset_relationship(self, context, dataset):
        relationship_dataset = None
        relationship_url = None
        try:
            toolkit.get_validator('package_name_exists')(dataset, context)
            relationship_dataset = dataset
        except toolkit.Invalid:
            # Dataset does not exist so must be an external dataset URL
            # Validation should have already happened in validator 'qdes_validate_related_dataset' so the dataset should be a URL to external dataset
            relationship_url = dataset

        return (relationship_dataset, relationship_url)

    def _update_related_resources(self, context, pkg_dict):
        data_dict = {"id": pkg_dict.get('id'), "related_resources": pkg_dict.get('related_resources')}
        toolkit.get_action('update_related_resources')(context, data_dict)
