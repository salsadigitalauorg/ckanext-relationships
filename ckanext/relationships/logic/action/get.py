import ckan.plugins.toolkit as toolkit
import logging


log = logging.getLogger(__name__)


@toolkit.chained_action
def package_relationships_list(original_action, context, data_dict):

    toolkit.check_access('package_relationships_list', context, data_dict)

    log.debug('>>> This is my functoin <<<<')
    log.debug('>>> This is my functoin <<<<')
    log.debug('>>> This is my functoin <<<<')
    log.debug('>>> This is my functoin <<<<')

    model = context['model']
    # id = _get_or_bust(data_dict, "id")

    return {}
