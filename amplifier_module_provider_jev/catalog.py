"""Offline metadata; does not construct a client or read credentials."""
def catalog():
    from amplifier_decisions.config import validate
    return {'schema_version': 2, 'provider_module': 'provider-jev', 'validate': validate,
            'backends': [{'kind': 'jev', 'label': 'Jev', 'default_model': 'jev-1.14.0',
                          'decision_only': True, 'connection': {'auth': 'key',
                              'description': 'Use a TypeSafe key for optional browser and computer decisions.'},
                          'models': ['jev-1.14.0', 'jev-latest'], 'configuration_key': 'decisions'}]}
