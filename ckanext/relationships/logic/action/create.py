import ckan.plugins.toolkit as toolkit
import logging

from ckan.logic import auth_allow_anonymous_access, NotFound
from ckan.model import meta
log = logging.getLogger(__name__)


@auth_allow_anonymous_access
@toolkit.chained_action
def package_relationship_create(original_action, context, data_dict):
    # toolkit.check_access('site_read', context)
    toolkit.check_access('package_relationship_create', context, data_dict)

    # @TODO: check if data_dict -> object is None
    # if so, we try to add a relationship without object-id
    log.debug('#### data_dict ####')
    log.debug('#### data_dict ####')
    log.debug(data_dict)
    log.debug('#### data_dict ####')
    log.debug('#### data_dict ####')

    object_id = data_dict.get('object', None)

    if not object_id:
        log.debug('... No object ...')
        log.debug('... No object ...')
        log.debug('... No object ...')

        model = context['model']

        subject = data_dict.get('subject', None)
        type = data_dict.get('type', None)
        comment = data_dict.get('comment', u'')

        pkg1 = model.Package.get(subject)

        if not pkg1:
            raise NotFound('Subject package %r was not found.' % subject)
        # @TODO: handle existing relationships with an external URI

        from ckan.model import package_relationship

        rel = package_relationship.PackageRelationship(
            subject=pkg1,
            object=None,
            type=type,
            comment=comment)

        meta.Session.add(rel)
        meta.Session.commit()

        # rel = pkg1.add_relationship(rel_type, pkg2, comment=comment)
        # if not context.get('defer_commit'):
        #     model.repo.commit_and_remove()
        # context['relationship'] = rel

    # else We revert to the parent action
    else:
        log.debug('... REVERTING to core CKAN package_relationship_create ...')
        log.debug('... REVERTING to core CKAN package_relationship_create ...')
        log.debug('... REVERTING to core CKAN package_relationship_create ...')
        log.debug('... REVERTING to core CKAN package_relationship_create ...')

    return True
