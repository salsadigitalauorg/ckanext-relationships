import ckan.plugins.toolkit as toolkit
import logging

from ckan.logic import auth_allow_anonymous_access, NotFound
from ckan.model import meta
from ckan.model.package_relationship import PackageRelationship
from ckanext.qdes_schema import validators

log = logging.getLogger(__name__)


@auth_allow_anonymous_access
@toolkit.chained_action
def package_relationship_create(original_action, context, data_dict):
    toolkit.check_access('package_relationship_create', context, data_dict)
    model = context['model']
    object_id = data_dict.get('object', None)
    subject = data_dict.get('subject', None)
    relationship_type = data_dict.get('type', None)

    # If data_dict -> object_id is None, we try to add a package_relationship record without `object_package_id`
    if not object_id:
        comment = data_dict.get('comment', u'') or None  # Just in case it is an empty string

        pkg1 = model.Package.get(subject)

        if not pkg1:
            raise NotFound('>>> Subject package {0} was not found.'.format(subject))

        if comment:
            # Check if a matching external URI relationship already exists
            # otherwise we'd end up creating a duplicate
            existing_relationship = toolkit.get_action('get_package_relationship_by_uri')(context, {
                'id': subject,
                'uri': comment,
                'type': relationship_type,
            })

            if not existing_relationship:
                relationship = PackageRelationship(
                    subject=pkg1,
                    object=None,
                    type=relationship_type,
                    comment=comment)

                meta.Session.add(relationship)
                meta.Session.commit()

            # rel = pkg1.add_relationship(rel_type, pkg2, comment=comment)
            # if not context.get('defer_commit'):
            #     model.repo.commit_and_remove()
            # context['relationship'] = rel

    # else We revert to the parent/CKAN core `package_relationship_create` action
    else:
        log.info('*** Reverting to core CKAN package_relationship_create for:')
        log.info(data_dict)
        try:
            # qdes_validate_circular_replaces_relationships(current_dataset_id, relationship_dataset_id, relationship_type, context):
            # Validates the dataset relationship to prevent circular reference
            validators.qdes_validate_circular_replaces_relationships(subject, object_id, relationship_type, context)
            original_action(context, data_dict)
        except toolkit.Invalid as ex:
            log.warning(ex)

    return True
