from vent.api.plugin_helpers import PluginHelper


def test_get_path():
    """ Test the get_path function """
    instance = PluginHelper()
    path = instance.get_path('https://github.com/cyberreboot/vent')
    assert path.endswith('.internals/plugins/cyberreboot/vent')
    path = instance.get_path('https://github.com/cyberreboot/vent-plugins')
    assert '.internals' not in path

def test_apply_path():
    """ Test the apply_path function """
    instance = PluginHelper()
    status = instance.apply_path('https://github.com/cyberreboot/vent')
    assert isinstance(status, tuple)
    assert status[0] == False
    status = instance.apply_path('https://github.com/cyberreboot/vent.git')
    assert isinstance(status, tuple)
    assert status[0] == False

def test_checkout():
    """ Test the checkout function """
    instance = PluginHelper()
    status = instance.checkout()
    assert isinstance(status, tuple)
    assert status[0] == True

def test_available_tools():
    """ Test the available_tools function """
    instance = PluginHelper()
    path = instance.get_path('https://github.com/cyberreboot/vent')
    matches = instance.available_tools(path)
    assert isinstance(matches, list)
