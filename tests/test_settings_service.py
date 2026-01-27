from services import settings_service




def test_set_and_get_setting(test_db):
    settings_service.set_setting('site_name', 'My Test Shop')
    assert settings_service.get_setting('site_name') == 'My Test Shop'




def test_initialize_defaults(test_db):
    defaults = {'lang': 'ur', 'default_currency': 'PKR'}
    settings_service.initialize_defaults(defaults)
    # calling again should not overwrite
    settings_service.set_setting('lang', 'en')
    settings_service.initialize_defaults({'lang': 'ur'})
    assert settings_service.get_setting('lang') == 'en'