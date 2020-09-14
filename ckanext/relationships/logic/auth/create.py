import ckan.authz as authz
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


#@toolkit.chained_auth_function
def package_relationship_create(context, data_dict):
    # Copied from CKAN core logic/auth/create.py
    user = context['user']

    id = data_dict['subject']
    # @TODO: add check for 'object' - if it exists - call the parent auth function?
    # id2 = data_dict['object']

    # If we can update each package we can see the relationships
    authorized1 = authz.is_authorized_boolean(
        'package_update', context, {'id': id})
    # authorized2 = authz.is_authorized_boolean(
    #     'package_update', context, {'id': id2})

    # if not (authorized1 and authorized2):
    if not authorized1:
        # return {'success': False, 'msg': _('User %s not authorized to edit these packages') % user}
        return {'success': False, 'msg': _('User %s not authorized to edit this package') % user}
    else:
        return {'success': True}
