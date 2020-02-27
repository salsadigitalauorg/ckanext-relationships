import ckan.lib.base as base
import ckan.logic as logic
import ckan.model as model

from ckan.common import c

abort = base.abort
get_action = logic.get_action


def get_relationships(id):
    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'auth_user_obj': c.userobj}

    relationships = get_action('package_relationships_list')(context, {'id': id})

    # from pprint import pprint
    # pprint(relationships)

    if relationships:
        try:

            for relationship in relationships:
                package = get_action('package_show')(context, {'id': relationship['object']})
                if package:
                    relationship['title'] = package['title']
        except Exception, e:
            print(str(e))

        return relationships
    else:
        return []


def get_relatable_datasets(id):

    relatable_datasets = []

    context = {'model': model, 'session': model.Session,
               'user': c.user, 'for_view': True,
               'auth_user_obj': c.userobj}

    data_dict = {'q': '', 'limit': 1000}

    try:
        source_package = get_action('package_show')(context, {'id': id})
        packages = get_action('package_autocomplete')(context, data_dict)
    except Exception:
        abort(404, _('An issue occurred'))

    if packages:
        # get the current relationships, so we can exclude those datasets from the list
        existing_relationships = [relationship['object'] for relationship in get_relationships(id)]

        for package in packages:
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
    except Exception, e:
        abort(404, str(e))

    return ''
