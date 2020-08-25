import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckan.model.package_relationship import PackageRelationship
from ckanext.relationships import blueprint, helpers


class RelationshipsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')

    # IRoutes

    def before_map(self, map):
        # map.connect('dataset_relationships', '/dataset/{id}/relationships',
        #             controller='ckanext.relationships.controller:RelationshipController',
        #             action='dataset_relationships',
        #             ckan_icon='pencil-square-o'
        #             )
        # map.connect('create_dataset_relationship', '/dataset/{id}/relationships/create',
        #             controller='ckanext.relationships.controller:RelationshipController',
        #             action='create_dataset_relationship'
        #             )
        map.connect('delete_dataset_relationship', '/dataset/{id}/relationships/delete/{type}/{object}',
                    controller='ckanext.relationships.controller:RelationshipController',
                    action='delete_dataset_relationship'
                    )
        return map

    # ITemplateHelpers
    def get_helpers(self):
        return {
            'get_relationships': helpers.get_relationships,
            'get_relatable_datasets': helpers.get_relatable_datasets,
            'get_lineage_notes': helpers.get_lineage_notes,
            'get_relationship_types': helpers.get_relationship_types,
        }

    # IBlueprint

    def get_blueprint(self):
        return blueprint.relationships

    # IConfigurable

    def configure(self, config):
        PackageRelationship.types.append(
            (u'is_part_of', u'has_part')
        )
