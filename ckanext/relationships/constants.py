# TODO: Needs to load the vocabulary service for 'nature of relationship' and parse it into forward/reverse relationship types somehow before overriding the PackageRelationship.types variable
# Implement after this story has completed https://it-partners.atlassian.net/browse/DDCI-40
RELATIONSHIP_TYPES = [
    (u'unspecified relationship', u''),
    (u'hasPart', u'isPartOf'),
    (u'isPartOf', u'hasPart'),
    (u'isFormatOf', u'hasFormat'),
    (u'hasFormat', u'isFormatOf'),
    (u'isVersionOf', u'hasVersion'),
    (u'hasVersion', u'isVersionOf'),
    (u'replaces', u'isReplacedBy'),
    (u'isReplacedBy', u'replaces'),
    (u'references', u'isReferencedBy'),
    (u'isReferencedBy', u'references'),
    (u'requires', u'isRequiredBy'),
    (u'isRequiredBy', u'requires'),
]
