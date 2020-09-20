import ckan.lib.base as base
import ckan.lib.search as search
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging

from ckan.common import _, c, g
from ckan.model.package_relationship import PackageRelationship
from ckanext.qdes_schema.logic.helpers import relationship_helpers
from pprint import pprint

abort = base.abort
get_action = logic.get_action
log = logging.getLogger(__name__)


def get_relationships(id, context=None):
    # This appears to be needed for the click command...
    # ckan search-index rebuild
    # ...to work
    if not context:
        user = logic.get_action(u'get_site_user')(
            {u'model': model, u'ignore_auth': True}, {})
        context = {u'model': model, u'session': model.Session,
                    u'user': user[u'name']}

    try:
        relationships = get_action('package_relationships_list')(context, {'id': id})
    except Exception as e:
        log.error(str(e))
        # whatever
        # @TODO: why does it not throw an exception here?

    if relationships:
        try:
            for relationship in relationships:
                # log.debug(relationship)
                if relationship['object']:
                    # QDES: handle standard CKAN dataset to dataset relationships
                    package = get_action('package_show')(context, {'id': relationship['object']})
                    if package:
                        relationship['title'] = package['title']
                else:
                    # QDES: handle CKAN dataset to EXTERNAL URI relationships
                    relationship['title'] = relationship['comment']
        except Exception as e:
            print(str(e))

        return relationships
    else:
        return []


def get_relatable_datasets(id):

    relatable_datasets = []

    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'ignore_auth': True,
               'auth_user_obj': c.userobj}

    data_dict = {'q': 'dsafdsafdsa', 'limit': 1000}

    try:
        source_package = get_action('package_show')(context, {'id': id})
        #packages = get_action('package_autocomplete')(context, data_dict)

        # this is copied from ckan/ckan_core/ckan/logic/action/get.py
        # and adjusted to retrieve ALL packages for now
        # until we can figure out how to send a wildcard query
        limit = data_dict.get('limit', 10)
        q = data_dict['q']
        labels = None
        data_dict = {
            # 'q': ' OR '.join([
            #     'name_ngram:{0}',
            #     'title_ngram:{0}',
            #     'name:{0}',
            #     'title:{0}',
            # ]).format(search.query.solr_literal(q)),
            'fl': 'name,title',
            'rows': limit
        }
        query = search.query_for(model.Package)

        results = query.run(data_dict, permission_labels=labels)['results']

        q_lower = q.lower()
        pkg_list = []
        for package in results:
            if q_lower in package['name']:
                match_field = 'name'
                match_displayed = package['name']
            else:
                match_field = 'title'
                match_displayed = '%s (%s)' % (package['title'], package['name'])
            result_dict = {
                'name': package['name'],
                'title': package['title'],
                'match_field': match_field,
                'match_displayed': match_displayed}
            pkg_list.append(result_dict)

    except Exception:
        abort(404, _('An issue occurred'))

    if pkg_list:
        # get the current relationships, so we can exclude those datasets from the list
        existing_relationships = [relationship['object'] for relationship in get_relationships(id)]

        for package in pkg_list:
            if package['name'] != source_package['name'] and package['name'] not in existing_relationships:
                relatable_datasets.append(
                    {
                        'name': package['name'],
                        'title': package['title']
                    }
                )

    return relatable_datasets


def get_lineage_notes(type, object):
    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'auth_user_obj': c.userobj}
    try:
        source_package = get_action('package_show')(context, {'id': object})
        return source_package.get('lineage', None)
    except Exception as e:
        abort(404, str(e))

    return ''


def get_relationship_types(field=None):
    types = PackageRelationship.types
    return types


def get_relationship_types_as_flat_list():
    relationship_types = []

    relationship_type_pairs = get_relationship_types()

    for pair in relationship_type_pairs:
        for value in pair:
            if value:
                relationship_types.append(value)

    return relationship_types


def quote_uri(uri):
    from urllib.parse import quote
    return quote(uri, safe='')


def unquote_uri(uri):
    from urllib.parse import unquote
    return unquote(uri)


# @TODO: Should this be moved into the `ckanext-qdes-schema` extension? YES
def reconcile_package_relationships(context, pkg_id, related_resources):
    """
    Only delete package relationships for the dataset when the relationship
    no longer exists in the `related_resources` field

    Called on IPackageController `after_update`

    :param context:
    :param pkg_id: package/dataset ID
    :return:
    """
    existing_relationships = get_action('subject_package_relationship_objects')(context, {'id': pkg_id})

    # `related_resources` might be an empty string
    related_resources = related_resources or None

    # If `related_resources` is empty - it indicates that all related resources have been removed from the dataset
    if not related_resources:
        # Delete ALL existing relationships for this dataset
        log.debug('Deleting ALL package_relationship records for dataset id {0}'.format(pkg_id))
        get_action('package_relationship_delete_all')(context, {'id': pkg_id})
    else:
        # Convert the `related_resources` JSON string into a more usable structure
        related_resources = relationship_helpers.convert_related_resources_to_dict_list(related_resources)

        # Check each existing relationship to see if it still exists in the dataset's related_resources
        # if not, delete it.
        for relationship in existing_relationships:
            matching_related_resource = None

            # If it's an external URI we can process straight away
            if not relationship.object_package_id:
                matching_related_resource = [resource for resource in related_resources
                                             if resource['relationship'] == relationship.type
                                             and resource['resource'] == relationship.comment]
            else:
                # If it's a CKAN dataset we need to fetch the package first to get the package name
                # @TODO: this seems kind of messy, i.e. should we be storing the CKAN package UUID?
                try:
                    related_pkg_dict = get_action('package_show')(context, {'id': relationship.object_package_id})

                    matching_related_resource = [resource for resource in related_resources
                                                 if resource['relationship'] == relationship.type
                                                 and resource['resource'] == related_pkg_dict['name']]
                except Exception as e:
                    log.error(str(e))

            if not matching_related_resource:
                # Delete the existing relationship from `package_relationships` as it no longer exists in the dataset
                relationship.purge()
                model.meta.Session.commit()


def show_relationships_on_dataset_detail():
    return toolkit.asbool(toolkit.config.get('ckanext.relationships.show_relationships_on_dataset_detail', True))
