"""
Test definitions in api module
"""


class FixturesMixin(object):
    """
    Fixture test to load data
    """
    fixtures = [
        'initial_data_api.json',
    ]
