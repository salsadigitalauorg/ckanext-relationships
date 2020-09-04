import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckan.model.package_relationship import PackageRelationship
from ckanext.relationships import blueprint, constants, helpers


class RelationshipsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurable, inherit=True)

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
        }

    # IBlueprint

    def get_blueprint(self):
        return blueprint.relationships

    # IConfigurable

    def configure(self, config):
        PackageRelationship.types = constants.RELATIONSHIP_TYPES
        # PackageRelationship.types.append(
        #     (u'isPartOf', u'hasPart')
        # )
        # PackageRelationship.types.append(
        #     (u'replaces', u'isReplacedBy')
        # )
        # PackageRelationship.types.append(
        #     (u'alternateOf', u'')
        # )
