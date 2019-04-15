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

To keep updated with new developments in the OpenStack project
follow `@openstack <http://twitter.com/openstack>`_ on Twitter.

To learn how to deploy OpenStack Nova, consult the documentation
available online at:

   http://docs.openstack.org

For information about the different compute (hypervisor) drivers
supported by Nova, read this page on the wiki:

   https://wiki.openstack.org/wiki/HypervisorSupportMatrix

In the unfortunate event that bugs are discovered, they should
be reported to the appropriate bug tracker. If you obtained
the software from a 3rd party operating system vendor, it is
often wise to use their own bug tracker for reporting problems.
In all other cases use the master OpenStack bug tracker,
available at:

   http://bugs.launchpad.net/nova

Developers wishing to work on the OpenStack Nova project should
always base their work on the latest Nova code, available from
the master GIT repository at:

   https://git.openstack.org/cgit/openstack/nova

Developers should also join the discussion on the mailing list,
at:

   http://lists.openstack.org/cgi-bin/mailman/listinfo/openstack-dev

Any new code must follow the development guidelines detailed
in the HACKING.rst file, and pass all unit tests. Further
developer focused documentation is available at:

   http://docs.openstack.org/developer/nova/

For information on how to contribute to Nova, please see the
contents of the CONTRIBUTING.rst file.

Add supervisor config file to manage nova-scheduler. location in the
etc/nova/supervisor_nova-scheduler.conf

New features:

    * nova-scheduler : 添加新的权重器, 基于负载和hash来计算, 以达到
      虚拟机实例均匀散列到同一zone下的不同计算节点上.

    * nova-compute   : 为libvirt添加网卡多队列功能, 每个虚拟机实例创建
      成功后, 默认开启网卡多队列.

-- End of broadcast
