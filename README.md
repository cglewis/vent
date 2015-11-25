vent
====

Network Visibility (an anagram)

download pre-compiled ISO
====

[releases](https://github.com/CyberReboot/vent/releases)


build the ISO
====

### build dependencies

```
docker
```

### getting the bits

```
git clone https://github.com/CyberReboot/vent.git
cd vent
```

### `Makefile` targets

There main target builds the vent ISO without any of the containers that will need to be built after the fact. This allows the ISO to be a mere 40MB.  If you use one of the `prebuilt` options it will also build all of the necessary containers and tarball them up.  You can then use the `vent` utility after the vent instance is created inside the local `images` directory specifying `tar` as an argument, and it will add the tarballs as docker images on the instance.

#### `make all`

This target (the default target if none is supplied) will build the ISO.

#### `make all-no-cache`

This will build the ISO, but it won't use cache.

#### `make vent`

This target will build the minimal image without building the containers and build/extract the ISO from the final result.

#### `make vent-prebuilt`

This target will build the minimal image as well as tarballs of all of the images after building all the containers and build/extract the ISO from the final result.

#### `make vent-no-cache`

This will build the same target, but it won't use cache.

#### `make vent-prebuilt-no-cache`

This will build the same target and the tarballs, but it won't use cache.

#### `make images`

This will build the containers and export them as tarballs into the images directory and then make a gzip of those tarballs.

#### `make install`

This will install `vent` and `vent-generic` into the path and can be used for loading in tarball images or copying up PCAPs or other files to a vent instance.

#### `make clean`

This will remove all of the tarballs and ISOs created from any of the build processes.

easy ways to build a VM out of the ISO
====

with docker-machine cli:

```
python -m SimpleHTTPServer
docker-machine create -d virtualbox --virtualbox-boot2docker-url http://localhost:8000/vent.iso vent
# other options to customize the size of the vm are available as well:
# --virtualbox-cpu-count "1"
# --virtualbox-disk-size "20000"
# --virtualbox-memory "1024"
docker-machine ssh vent
```

of course traditional ways of deploying an ISO work as well, including VMWare, OpenStack, and booting from it to install on bare metal.  a couple of things to note: it will automatically install and provision the disk and then restart when done.  vent runs in RAM, so changes need to be made under `/var/lib/docker` or `/var/lib/boot2docker` as those are persistent (see boot2docker [documentation](https://github.com/boot2docker/boot2docker/blob/master/README.md) for more information).  it's possible that `vent-management` won't automatically get added and run, if you run `docker ps` and it's not running execute `sudo /data/custom`.

getting started
====

from within the vent interface (once SSH'd in) first `build` the collectors (if you chose the `prebuilt` ISO this is already done for you, so you can skip this step).  it might take a little while to download and compile everything.

alternatively, if you want to access the vent interface from the console instead of SSHing in, you can run `vent` from the commandline.

once it's built you're ready to start the `collectors` from the `mode` menu option.

after starting, you should be able to go into `system info` and see that everything is running as expected.  once that looks good, you're ready to copy up pcaps.  that's it!

copy up new pcaps
====

if using docker-machine cli to provision:

```
# from the directory that contains your pcaps
# optionally add an argument of the name for vent in
#     docker-machine if you called it something other than vent
cd vent
cp vent /usr/local/bin/
cd /path/where/pcaps/are/
vent
```

if deploying as a self-configured machine (VMWare, OpenStack, bare metal, etc.):

```
# from the directory that contains your pcaps
# optionally add an argument of the name/ip for vent on your network
cd vent
cp vent-generic /usr/local/bin/vent
cd /path/where/pcaps/are/
vent
```

otherwise edit the `ssh` and `scp` lines in `vent` specific to docker-machine and change to suit your needs

copy up new templates and plugins
====

if using docker-machine cli to provision:

```
docker-machine scp modes.template vent:/var/lib/docker/data/templates/modes.template
```

if using boot2docker cli to provision (DEPRECATED):

```
scp -r -i ~/.ssh/id_boot2docker -P 2022 modes.template docker@localhost:/var/lib/docker/data/templates/modes.template
```

if deploying as a self-configured machine (VMWare, OpenStack, bare metal, etc.):

```
scp modes.template docker@vnet:/var/lib/docker/data/templates/modes.template
```

FAQ
====

**Q**: What are the credentials to login if I don't use certificates/keys?

**A**: docker/tcuser

**Q**: I went into the shell and did a `docker ps` but no containers are running, how do I get it working again?

**A**: execute `docker rm vent-management; sudo /data/custom`, if that doesn't work, restart the VM.

The following notes mirror that of [boot2docker](https://github.com/boot2docker/boot2docker)
====

#### Docker daemon options

If you need to customize the options used to start the Docker daemon, you can
do so by adding entries to the `/var/lib/boot2docker/profile` file on the
persistent partition inside the Boot2Docker virtual machine. Then restart the
daemon.

The following example will enable core dumps inside containers, but you can
specify any other options you may need.

```console
boot2docker ssh -t sudo vi /var/lib/boot2docker/profile
# Add something like:
#     EXTRA_ARGS="--default-ulimit core=-1"
boot2docker restart
```

#### Local Customisation (with persistent partition)

Changes outside of the `/var/lib/docker` and `/var/lib/boot2docker` directories
will be lost after powering down or restarting the boot2docker VM. However, if
you have a persistence partition (created automatically by `boot2docker init`),
you can make customisations that are run at the end of boot initialisation by
creating a script at ``/var/lib/boot2docker/bootlocal.sh``.

From Boot2Docker version 1.6.0, you can also specify steps that are run before
the Docker daemon is started, using `/var/lib/boot2docker/bootsync.sh`.

You can also set variables that will be used during the boot initialisation (after
the automount) by setting them in `/var/lib/boot2docker/profile`

For example, to download ``pipework``, install its pre-requisites (which you can
download using ``tce-load -w package.tcz``), and then start a container:

```
#!/bin/sh


if [ ! -e /var/lib/boot2docker/pipework ]; then
        curl -o /var/lib/boot2docker/pipework https://raw.github.com/jpetazzo/pipework/master/pipework
        chmod 777 /var/lib/boot2docker/pipework
fi

#need ftp://ftp.nl.netbsd.org/vol/2/metalab/distributions/tinycorelinux/4.x/x86/tcz/bridge-utils.tcz
#and iproute2 (and its friends)
su - docker -c "tce-load -i /var/lib/boot2docker/*.tcz"

#start my management container if its not already there
docker run -d -v /var/run/docker.sock:/var/run/docker.sock $(which docker):$(which docker)  -name dom0 svens-dom0
```

Or, if you need to tell the Docker daemon to use a specific DNS server, add the 
following to ``/var/lib/boot2docker/profile``:

```
EXTRA_ARGS="--dns 192.168.1.2"
```
