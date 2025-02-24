# OpenStack Nova

OpenStack Nova provides a cloud computing fabric controller, supporting a wide variety of virtualization technologies,
including KVM, Xen, LXC, VMware, and more. In addition to its native API, it includes compatibility with the commonly
encountered Amazon EC2 and S3 APIs.

OpenStack Nova is distributed under the terms of the Apache License, Version 2.0. The full terms and conditions of this
license are detailed in the LICENSE file.

Nova primarily consists of a set of Python daemons, though it requires and integrates with a number of native system
components for databases, messaging and virtualization capabilities.

## New Features

### nova-scheduler

- 添加新的权重器，基于负载和 hash 来计算，以达到虚拟机实例均匀散列到同一 zone 下的不同计算节点上。

### nova-compute

- 为 libvirt 添加网卡多队列功能，每个虚拟机实例创建成功后，默认开启网卡多队列。
- 去掉以太网防火墙配置，解决虚 IP 无法 ping 通。

### nova-conductor

- 分配 IP 时探测当前 IP 是否在用，如果在用则直接跳过，去拿下一个，以此类推。

### nova-network

- 创建 VLAN 网络时进行虚 IP 段预留。同时约定：
  - 最小 VLAN 段预留 5 个作为虚 IP。
  - 一个 C 段预留 10 个作为虚 IP。
  
- 支持同一 VLAN 多网段功能。
- `ip a show br401` 可以看到：同一 VLAN、不同网段的 DHCP IP 已经挂载到了网桥上。

## Rocky Linux

### 安装 `brctl`

```bash
wget https://vault.centos.org/7.9.2009/os/x86_64/Packages/bridge-utils-1.5-9.el7.x86_64.rpm
rpm -ivh bridge-utils-1.5-9.el7.x86_64.rpm
```

### Rocky 运行 nova-network

```bash
dnf install -y python2.x86_64
pip2 install virtualenv
virtualenv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py develop

tools/with_venv.sh nova-network --log-dir=/var/log/nova --log-file=nova-network.log --config-file=/etc/nova/nova.conf -v -d
```

### 容器运行 nova-compute

#### 构建镜像

```bash
# 目录及依赖
cd /opt/ && mkdir nova && cd nova/
git clone https://github.com/yolooks/kilo.git

# 创建Dockerfile
vim Dockerfile
FROM centos:centos7.9.2009

ARG timezone=Asia/Shanghai

ENV LIBGUESTFS_ATTACH_METHOD=appliance

COPY ./kilo/source /opt/source

RUN cp -f /usr/share/zoneinfo/${timezone} /etc/localtime && \
    cd /opt/source && \
    chmod +x install.sh && \
    ./install.sh

USER nova

CMD ["/usr/bin/nova-compute"]

# 构建镜像
docker build --network=host -t nova:1.0.0 .
```

#### 启动容器

```bash
# 启动容器
docker run -d --name nova-compute -v /data0:/data0 -v /etc/nova:/etc/nova -v /var/lib/nova:/var/lib/nova -v /var/run/libvirt:/var/run/libvirt -v /sys/fs/cgroup:/sys/fs/cgroup --cgroupns host --network host --pid host --uts host --ipc host --userns host --privileged nova:1.0.0

# 查看容器
docker ps -a

# 进入容器
docker exec -it nova-compute bash
```

#### 创建nova用户

```bash
useradd -M -u 162 nova
groupmod -g 162 nova
usermod -aG libvirt nova
usermod -aG docker nova
usermod -aG nobody nova
usermod -aG qemu nova
```

#### systemd管理

```bash
# systemd管理
vim /lib/systemd/system/openstack-nova-compute.service
[Unit]
Description=OpenStack Nova Compute Container
After=network.target libvirtd.service docker.service
Requires=docker.service

[Service]
User=nova
Restart=always
ExecStartPre=-/usr/bin/docker stop nova-compute
ExecStartPre=-/usr/bin/docker rm -f nova-compute
ExecStart=/usr/bin/docker run --name nova-compute \
    -v /data0:/data0 \
    -v /etc/nova:/etc/nova \
    -v /var/lib/nova:/var/lib/nova \
    -v /var/run/libvirt:/var/run/libvirt \
    -v /sys/fs/cgroup:/sys/fs/cgroup \
    --cgroupns host \
    --network host \
    --pid host \
    --uts host \
    --ipc host \
    --userns host \
    --privileged \
    nova:1.0.0
ExecStop=/usr/bin/docker stop nova-compute
ExecStopPost=/usr/bin/docker rm -f nova-compute

[Install]
WantedBy=multi-user.target

# 启动
systemctl daemon-reload
systemctl start openstack-nova-compute
systemctl enable openstack-nova-compute
```
