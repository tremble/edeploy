#!/bin/bash
KVM=
DISK=kvm_storage.img
DISK_SIZE=2000 # in MB
HTTP_PORT=9000
INST=$1
SSH_PORT=2222
PYTHON_PID=0
RSYNC_PID=0
LOCKFILE=edeploy.lock

detect_kvm() {
	VM=$(which kvm 2>/dev/null)
	if [ $? -ne 0 ]; then
		KVM=$(which qemu-kvm 2>/dev/null)
		if [ $? -ne 0 ]; then
			echo "Please Install KVM first"
			echo "Exiting !"
			exit 1
		fi
	fi
}

prepare_disk() {
	if [ ! -f $DISK ]; then
		echo "Preparing system disk, please wait a short"
		qemu-img create -f qcow2 $DISK ${DISK_SIZE}M
	fi
}

run_kvm() {
	BOOT_DEVICE="n"
	[ "$1" = "local" ] && BOOT_DEVICE="c"

	$KVM --enable-kvm -m 512\
		-netdev user,id=net0,net=10.0.2.0/24,tftp=tftpboot,bootfile=/pxelinux.510,hostfwd=tcp::$SSH_PORT-:22 \
		-netdev user,id=net1,net=10.0.3.0/24 \
		-netdev user,id=net2,net=1.2.3.0/24 \
		-device virtio-net,netdev=net0,mac=52:54:12:34:00:01 \
		-device virtio-net,netdev=net1,mac=52:54:12:34:00:02 \
		-device virtio-net,netdev=net2,mac=52:54:12:34:00:03 \
		-drive file=$DISK,if=virtio,id=drive-virtio-disk0,format=qcow2,cache=none,media=disk,index=0 \
		-boot $BOOT_DEVICE \
		-serial stdio \
		-smbios type=1,manufacturer=kvm,product=edeploy_test_vm
}


start_rsyncd() {
	cat > rsync-kvm.conf << EOF
use chroot = no
syslog facility = local5
pid file = rsyncd-edeploy.pid

[install]
	uid=root
	gid=root
	path=$INST/install

[metadata]
	uid=root
	gid=root
	path=$INST/metadata
EOF

	# Rsync shall die with the current test
	rsync --daemon --config rsync-kvm.conf --port 1515 --no-detach &
	RSYNC_PID=$!
}

start_httpd() {
	ln -sf ../ cgi-bin &>/dev/null
	python -m CGIHTTPServer $HTTP_PORT &
	HTTP_PID=$!
}

stop_httpd() {
	kill -9 $HTTP_PID &>/dev/null
	rm -f $LOCKFILE
}

stop_rsyncd() {
	kill -9 $RSYNC_PID &>/dev/null
	rm -f rsyncd-edeploy.pid &>/dev/null
}

create_edeploy_conf() {
	cat > edeploy.conf << EOF
[SERVER]

CONFIGDIR=$PWD/../config
LOCKFILE=$LOCKFILE
USEPXEMNGR=False
PXEMNGRURL=http://192.168.122.1:8000/
EOF

# Insure upload.py can create its lock file locally
chmod a+rw .
chmod a+rw $PWD/../config/state
chmod a+rw $PWD/../config/kvm-test.cmdb

ln -sf $PWD/edeploy.conf /etc/
}

############## MAIN
start_rsyncd
start_httpd
create_edeploy_conf
detect_kvm
prepare_disk
run_kvm
stop_httpd
stop_rsyncd
run_kvm local