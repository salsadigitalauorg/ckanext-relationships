import ckan.model as model
import ckan.plugins.toolkit as toolkit
import logging

log = logging.getLogger(__name__)


@toolkit.chained_action
def package_relationships_list(original_action, context, data_dict):

    toolkit.check_access('package_relationships_list', context, data_dict)

    relationship_dicts = []

    model = context['model']
    id = data_dict.get('id', None)

    # @TODO: needs to be wrapped in try / except to catch NotFound
    if id:
        dataset = model.Package.get(id)
        relationships = dataset.get_relationships()

        if relationships:
            # QDES: Implement our own `package.as_dict` method
            for relationship in relationships:
                if not relationship.object_package_id:
                    relationship_dicts.append(
                        {'subject': dataset,
                         'type': relationship.type,
                         'object': None,
                         'comment': relationship.comment}
                    )
                else:
                    log.debug('Normal CKAN package to package relationship')
                    relationship_dicts.append(relationship.as_dict(dataset))
        else:
            log.debug('>>>> NO Relationships <<<<<')
            log.debug('>>>> NO Relationships <<<<<')
            log.debug('>>>> NO Relationships <<<<<')
            log.debug('>>>> NO Relationships <<<<<')

    return relationship_dicts
