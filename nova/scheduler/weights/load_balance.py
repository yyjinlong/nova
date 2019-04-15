# -*- coding:utf-8 -*-
#
# Copyright @ 2018 OPS Inc.
#
# Author: Jinlong Yang
#

from oslo_config import cfg
from oslo_log import log as logging

from nova.scheduler import weights

load_weight_opts = [
    cfg.IntOpt('load_weight_multiplier',
               default=1,
               help='Multiplier used for weighing host load. Negative '
                    'numbers mean preference to choose light workload '
                    'compute hosts.'),
    cfg.IntOpt('instance_threshold',
               default=13,
               help='An threshold value used for hash calculate. Hash '
                    'result ensure the less instance count of compute '
                    'node that fetch greater weight value. Here，we '
                    'assume that online compute node most assigned '
                    '13 virtual machine instance.')
]

CONF = cfg.CONF
CONF.register_opts(load_weight_opts)

LOG = logging.getLogger(__name__)


class LoadBalanceWeigher(weights.BaseHostWeigher):
    minval = 0

    def weight_multiplier(self):
        """Override the weight multiplier."""
        return CONF.load_weight_multiplier

    def _weigh_object(self, host_state, weight_properties):
        weigh = 0

        # NOTE(根据已分配实例数量进行hash运算, 尽量保证均匀.)
        hypervisor = host_state.nodename
        num_instances = host_state.num_instances
        LOG.info('** Load balance fetch hypervisor: %s instance count: %s'
                  % (hypervisor, num_instances))
        threshold = CONF.instance_threshold
        hash_result = threshold - hash(num_instances) % threshold
        weigh += hash_result

        # NOTE(负载越高, 对应的权重值越低.)
        io_ops = host_state.num_io_ops
        if io_ops > 0:
            weigh -= io_ops
        LOG.info('** Load balance fetch hypervisor: %s io ops: %s'
                  % (hypervisor, io_ops))

        LOG.info('** Load balance fetch hypervisor: %s calculate weigh: %s'
                  % (hypervisor, weigh))
        return weigh
