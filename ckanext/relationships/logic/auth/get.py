import ckan.authz as authz
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


# @TODO: chain this up to the parent
#@toolkit.chained_auth_function
def package_relationships_list(context, data_dict):
    """This is largely copied from the core CKAN auth function"""

    log.debug('>>>> My package_relationships_list AUTH function <<<<')
    log.debug('>>>> My package_relationships_list AUTH function <<<<')

    user = context.get('user')

    id = data_dict['id']

    # @TODO: Implementation for relationship WITHOUT object

    # @TODO: Pass to parent auth method for relationships WITH object

    return {'success': True}
