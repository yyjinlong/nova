OpenStack Nova README
=====================

OpenStack Nova provides a cloud computing fabric controller,
supporting a wide variety of virtualization technologies,
including KVM, Xen, LXC, VMware, and more. In addition to
its native API, it includes compatibility with the commonly
encountered Amazon EC2 and S3 APIs.

OpenStack Nova is distributed under the terms of the Apache
License, Version 2.0. The full terms and conditions of this
license are detailed in the LICENSE file.

Nova primarily consists of a set of Python daemons, though
it requires and integrates with a number of native system
components for databases, messaging and virtualization
capabilities.


New Features
============

nova-scheduler
------------------

- 添加新的权重器，基于负载和 hash 来计算，以达到虚拟机实例均匀散列到同一 zone 下的不同计算节点上。

nova-compute
----------------

- 为 libvirt 添加网卡多队列功能，每个虚拟机实例创建成功后，默认开启网卡多队列。
- 去掉以太网防火墙配置，解决虚 IP 无法 ping 通。

nova-conductor
------------------

- 分配 IP 时探测当前 IP 是否在用，如果在用则直接跳过，去拿下一个，以此类推。

nova-network
----------------

- 创建 VLAN 网络时进行虚 IP 段预留。同时约定：
  
  - 最小 VLAN 段预留 5 个作为虚 IP。
  - 一个 C 段预留 10 个作为虚 IP。

- 支持同一 VLAN 多网段功能。
- `ip a show br401` 可以看到：同一 VLAN、不同网段的 DHCP IP 已经挂载到了网桥上。

.. code-block:: mysql

   #登录nova数据库，删除唯一索引：
   MySQL [(none)]> use nova
   MySQL [(none)]> show create table networks;
   ...
   UNIQUE KEY `uniq_networks0vlan0deleted` (`vlan`,`deleted`),
   ...
   MySQL [(none)]> alter table networks DROP INDEX uniq_networks0vlan0deleted;

