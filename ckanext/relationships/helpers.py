import ckan.lib.base as base
import ckan.lib.search as search
import ckan.logic as logic
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging

from ckan.common import _, c, g
from ckan.model.package_relationship import PackageRelationship
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
    types = PackageRelationship.get_all_types()
    return types


def quote_uri(uri):
    from urllib.parse import quote
    return quote(uri, safe='')


def unquote_uri(uri):
    from urllib.parse import unquote
    return unquote(uri)


def get_subject_package_relationship_objects(id):
    try:
        relationships = get_action('subject_package_relationship_objects')({}, {'id': id})
    except Exception as e:
        log.error(str(e))
    relationship_dicts = []
    if relationships:
        try:
            for relationship in relationships:
                if not relationship.object_package_id:
                    relationship_dicts.append(
                        {'subject': id,
                         'type': relationship.type,
                         'object': None,
                         'comment': relationship.comment}
                    )
                else:
                    # Normal CKAN package to package relationship
                    relationship_dicts.append(relationship.as_dict())

            for relationship_dict in relationship_dicts:
                if relationship_dict['object']:
                    # QDES: handle standard CKAN dataset to dataset relationships
                    site_user = get_action(u'get_site_user')({u'ignore_auth': True}, {})
                    context = {u'user': site_user[u'name']}
                    package = get_action('package_show')(context, {'id': relationship_dict['object']})
                    if package:
                        deleted = ' [Deleted]' if package.get('state') == 'deleted' else ''
                        relationship_dict['title'] = package['title'] + deleted
                else:
                    # QDES: handle CKAN dataset to EXTERNAL URI relationships
                    relationship_dict['title'] = relationship_dict['comment']
        except Exception as e:
            log.error(str(e))

    return relationship_dicts


def show_relationships_on_dataset_detail():
    return toolkit.asbool(toolkit.config.get('ckanext.relationships.show_relationships_on_dataset_detail', True))
