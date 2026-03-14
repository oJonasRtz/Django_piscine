# How to create shared folder

## Host

- On virtualbox open settings/shared folders
- Click on +
- Foder Path: host path
- Folder Name: vm folder name
- [x]Auto-mount: auto mount at boot

## Virtual Machine
- `mkdir -p ~/shared`: Create the mount point inside de VM
-  `sudo mount -t vboxsf -o uid=$(id -u),gid=$(id -g) shared ~/shared` Mount for user access
- `sudo mount -t vboxsf <Folder Name> ~/shared`

### Notes

- Make sure VirtualBox Guest Additions are installed in the VM to use `vboxsf`
- How to check: `lsmod | grep vboxsf`
- How to install:
```
sudo apt update

sudo apt install build-essential dkms linux-headers-$(uname -r) virtualbox-guest-dkms virtualbox-guest-utils virtualbox-guest-x11

sudo reboot
```