# TODO: Needs to load the vocabulary service for 'nature of relationship' and parse it into forward/reverse relationship types somehow before overriding the PackageRelationship.types variable
# Implement after this story has completed https://it-partners.atlassian.net/browse/DDCI-40
RELATIONSHIP_TYPES = [
    (u'unspecified relationship', u'unspecified relationship'),
    (u'Is Part Of', u'Has Part'),
    (u'Is Format Of', u'Has Format'),
    (u'Is Version Of', u'Has Version'),
    (u'Replaces', u'Is Replaced By'),
    (u'References', u'Is Referenced By'),
    (u'Requires', u'Is Required By'),
    (u'Was Derived From', u'Was Derivation of'),
    (u'Was Influenced By', u'Influenced'),
    (u'Quoted As', u'Quoted From'),
    (u'Was Revision Of', u'Had Revision'),
    (u'Is Alternate Of', u'Is Alternate Of'),
    (u'Is Specialization Of', u'Is Generalization Of'),
]
