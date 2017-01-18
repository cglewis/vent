from vent.api.plugins import Plugin

def test_add():
    """ Test the add function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = instance.add('https://github.com/cyberreboot/vent', build=False)
    assert status[0] == True
    status = instance.add('https://github.com/cyberreboot/vent.git', build=True)
    assert status[0] == True
    bad_instance = Plugin()
    status = bad_instance.add('https://github.com/cyberreboot/vent', build=False)
    assert status[0] == False

def test_build_tools():
    """ Test the build_tools function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    status = instance.build_tools(0)
    assert status[0] == False
    status = instance.build_tools(128)
    assert status[0] == False
    status = instance.build_tools(255)
    assert status[0] == False
    status = instance.build_tools(-1)
    assert status[0] == False

def test_get_tool_matches():
    """ Test the get_tool_matches function """
    instance = Plugin(base_dir='/tmp/', vent_dir='/tmp/', vendor_dir='/tmp/', scripts_dir='/tmp/')
    matches = instance.get_tool_matches()
    assert matches == []
