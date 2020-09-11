import ckan.plugins.toolkit as toolkit
import logging
import json

log = logging.getLogger(__name__)


def update_related_resources(context, data_dict):
    """
    Update dataset related_resources metadata field
    """
    toolkit.check_access('package_update', context, data_dict)

    dataset_id = data_dict.get('id', None)
    if dataset_id:
        model = context.get('model')
        try:
            dataset = model.Package.get(dataset_id)
            if dataset:
                current_related_resources = dataset._extras.get('related_resources', None)
                new_related_resources_value = json.dumps(data_dict.get('related_resources', None)) if isinstance(
                    data_dict.get('related_resources', None), dict) else data_dict.get('related_resources', None)
                if current_related_resources and current_related_resources.value != new_related_resources_value:
                    current_related_resources.value = new_related_resources_value
                # Always set the below values to None as they should have been included above in related_resources
                series_or_collection = dataset._extras.get('series_or_collection', None)
                if series_or_collection:
                    series_or_collection.value = None
                related_datasets = dataset._extras.get('related_datasets', None)
                if related_datasets:
                    related_datasets.value = None

                dataset.commit()

        except Exception as e:
            log.error(str(e))
