from fabric.api import run, env, settings, quiet


def get_interfaces():
    with settings(quiet()):
        return run('ifconfig -l').strip().split()


def get_realmem():
    import math
    with settings(quiet()):
        realmem = run('sysctl -n hw.realmem').strip()
    realmem = float(realmem) / 1024 / 1024
    return 2 ** int(math.ceil(math.log(realmem, 2)))


def get_devices():
    """ computes the name of the disk devices that are suitable
    installation targets by subtracting CDROM- and USB devices
    from the list of total mounts.
    """
    with settings(quiet()):
        mounts = run('mount')
        sysctl_devices = run('sysctl -n kern.disks').strip().split()
    cd_device = env.instance.config.get('bootstrap-cd-device', 'cd0')
    if '/dev/{dev} on /rw/cdrom'.format(dev=cd_device) not in mounts:
        run('test -e /dev/{dev} && mount_cd9660 /dev/{dev} /cdrom || true'.format(dev=cd_device))
    usb_device = env.instance.config.get('bootstrap-usb-device', 'da0a')
    if '/dev/{dev} on /rw/media'.format(dev=usb_device) not in mounts:
        run('test -e /dev/{dev} && mount -o ro /dev/{dev} /media || true'.format(dev=usb_device))

    install_devices = [cd_device, usb_device]

    devices = set(sysctl_devices)
    for sysctl_device in sysctl_devices:
        for install_device in install_devices:
            if install_device.startswith(sysctl_device):
                devices.remove(sysctl_device)

    return devices
