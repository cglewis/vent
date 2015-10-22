def pcap_queue(path):
    import os
    import time

    import ConfigParser
    config = ConfigParser.RawConfigParser()

    from docker import Client
    c = Client(base_url='unix://var/run/docker.sock')

    responses = {}

    template_dir = "/data/templates/"
    plugins_dir = "/data/plugins/"
    try:
        config.read(template_dir+'modes.template')
        plugin_array = config.options("plugins")
        plugins = {}
        for plug in plugin_array:
            if plug != "collectors" and plug != "visualization":
                plugins[plug] = config.get("plugins", plug)
        t = []
        for plugin in plugins:
            if plugins[plugin] == 'all':
                tools = [ name for name in os.listdir(plugins_dir+plugin) if os.path.isdir(os.path.join(plugins_dir+plugin, name)) ]
                for tool in tools:
                    t.append(plugin+'/'+tool)
            else:
                for tool in plugins[plugin].split(","):
                    t.append(plugin+'/'+tool)

        container_count = 0
        container_max = 50
        try:
            config.read(template_dir+'collectors.template')
            container_max = int(config.get("active-containers", "count"))
        except:
            pass
        for image in t:
            # check resources before creating container
            # wait until there are resources available
            container_count = len(c.containers(filters={'status':'running'}))
            while container_count >= container_max:
                time.sleep(5)
                container_count = len(c.containers(filters={'status':'running'}))
            # for plugin, create container and start it
            # !! TODO read params for create_container from the templates!
            try:
                container = c.create_container(image=image, volumes=["/pcaps"], environment=["PYTHONUNBUFFERED=0"], tty=True, stdin_open=True, command=path)
                config.read(template_dir+'collectors.template')
                locally_active = config.options("locally-active")
                flag = 0
                if "rabbitmq" in locally_active:
                    if config.get("locally-active", "rabbitmq") == "off":
                        external_array = config.options("external")
                        if "rabbitmq_host" in external_array:
                            rabbitmq_host = config.get("external", "rabbitmq_host")
                            flag = 1
                if flag:
                    response = c.start(container=container.get('Id'), binds=["/pcaps:/pcaps:ro"], extra_hosts={"rabbitmq":rabbitmq_host})
                else:
                    response = c.start(container=container.get('Id'), binds=["/pcaps:/pcaps:ro"], links={"collectors-rabbitmq":"rabbitmq"})
                responses[image] = response
            except:
                pass
    except:
        pass
    return responses
