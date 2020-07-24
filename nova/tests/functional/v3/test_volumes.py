# Copyright 2012 Nebula, Inc.
# Copyright 2014 IBM Corp.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import datetime

from nova.compute import api as compute_api
from nova.compute import manager as compute_manager
from nova import context
from nova import db
from nova import objects
from nova.tests.functional.v3 import api_sample_base
from nova.tests.functional.v3 import test_servers
from nova.tests.unit.api.openstack import fakes
from nova.tests.unit import fake_block_device
from nova.tests.unit import fake_instance
from nova.volume import cinder


class SnapshotsSampleJsonTests(api_sample_base.ApiSampleTestBaseV3):
    extension_name = "os-volumes"

    create_subs = {
            'snapshot_name': 'snap-001',
            'description': 'Daily backup',
            'volume_id': '521752a6-acf6-4b2d-bc7a-119f9148cd8c'
    }

    def setUp(self):
        super(SnapshotsSampleJsonTests, self).setUp()
        self.stubs.Set(cinder.API, "get_all_snapshots",
                       fakes.stub_snapshot_get_all)
        self.stubs.Set(cinder.API, "get_snapshot", fakes.stub_snapshot_get)

    def _create_snapshot(self):
        self.stubs.Set(cinder.API, "create_snapshot",
                       fakes.stub_snapshot_create)

        response = self._do_post("os-snapshots",
                                 "snapshot-create-req",
                                 self.create_subs)
        return response

    def test_snapshots_create(self):
        response = self._create_snapshot()
        self.create_subs.update(self._get_regexes())
        self._verify_response("snapshot-create-resp",
                              self.create_subs, response, 200)

    def test_snapshots_delete(self):
        self.stubs.Set(cinder.API, "delete_snapshot",
                       fakes.stub_snapshot_delete)
        self._create_snapshot()
        response = self._do_delete('os-snapshots/100')
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, '')

    def test_snapshots_detail(self):
        response = self._do_get('os-snapshots/detail')
        subs = self._get_regexes()
        self._verify_response('snapshots-detail-resp', subs, response, 200)

    def test_snapshots_list(self):
        response = self._do_get('os-snapshots')
        subs = self._get_regexes()
        self._verify_response('snapshots-list-resp', subs, response, 200)

    def test_snapshots_show(self):
        response = self._do_get('os-snapshots/100')
        subs = {
            'snapshot_name': 'Default name',
            'description': 'Default description'
        }
        subs.update(self._get_regexes())
        self._verify_response('snapshots-show-resp', subs, response, 200)


class VolumesSampleJsonTest(test_servers.ServersSampleBase):
    extension_name = "os-volumes"

    def _get_volume_id(self):
        return 'a26887c6-c47b-4654-abb5-dfadf7d3f803'

    def _stub_volume(self, id, displayname="Volume Name",
                     displaydesc="Volume Description", size=100):
        volume = {
                  'id': id,
                  'size': size,
                  'availability_zone': 'zone1:host1',
                  'instance_uuid': '3912f2b4-c5ba-4aec-9165-872876fe202e',
                  'mountpoint': '/',
                  'status': 'in-use',
                  'attach_status': 'attached',
                  'name': 'vol name',
                  'display_name': displayname,
                  'display_description': displaydesc,
                  'created_at': datetime.datetime(2008, 12, 1, 11, 1, 55),
                  'snapshot_id': None,
                  'volume_type_id': 'fakevoltype',
                  'volume_metadata': [],
                  'volume_type': {'name': 'Backup'}
                  }
        return volume

    def _stub_volume_get(self, context, volume_id):
        return self._stub_volume(volume_id)

    def _stub_volume_delete(self, context, *args, **param):
        pass

    def _stub_volume_get_all(self, context, search_opts=None):
        id = self._get_volume_id()
        return [self._stub_volume(id)]

    def _stub_volume_create(self, context, size, name, description, snapshot,
                       **param):
        id = self._get_volume_id()
        return self._stub_volume(id)

    def setUp(self):
        super(VolumesSampleJsonTest, self).setUp()
        fakes.stub_out_networking(self.stubs)
        fakes.stub_out_rate_limiting(self.stubs)

        self.stubs.Set(cinder.API, "delete", self._stub_volume_delete)
        self.stubs.Set(cinder.API, "get", self._stub_volume_get)
        self.stubs.Set(cinder.API, "get_all", self._stub_volume_get_all)

    def _post_volume(self):
        subs_req = {
                'volume_name': "Volume Name",
                'volume_desc': "Volume Description",
        }

        self.stubs.Set(cinder.API, "create", self._stub_volume_create)
        response = self._do_post('os-volumes', 'os-volumes-post-req',
                                 subs_req)
        subs = self._get_regexes()
        subs.update(subs_req)
        self._verify_response('os-volumes-post-resp', subs, response, 200)

    def test_volumes_show(self):
        subs = {
                'volume_name': "Volume Name",
                'volume_desc': "Volume Description",
        }
        vol_id = self._get_volume_id()
        response = self._do_get('os-volumes/%s' % vol_id)
        subs.update(self._get_regexes())
        self._verify_response('os-volumes-get-resp', subs, response, 200)

    def test_volumes_index(self):
        subs = {
                'volume_name': "Volume Name",
                'volume_desc': "Volume Description",
        }
        response = self._do_get('os-volumes')
        subs.update(self._get_regexes())
        self._verify_response('os-volumes-index-resp', subs, response, 200)

    def test_volumes_detail(self):
        # For now, index and detail are the same.
        # See the volumes api
        subs = {
                'volume_name': "Volume Name",
                'volume_desc': "Volume Description",
        }
        response = self._do_get('os-volumes/detail')
        subs.update(self._get_regexes())
        self._verify_response('os-volumes-detail-resp', subs, response, 200)

    def test_volumes_create(self):
        self._post_volume()

    def test_volumes_delete(self):
        self._post_volume()
        vol_id = self._get_volume_id()
        response = self._do_delete('os-volumes/%s' % vol_id)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, '')


class VolumeAttachmentsSampleBase(test_servers.ServersSampleBase):
    def _stub_db_bdms_get_all_by_instance(self, server_id):

        def fake_bdms_get_all_by_instance(context, instance_uuid,
                                          use_subordinate=False):
            bdms = [
                fake_block_device.FakeDbBlockDeviceDict(
                {'id': 1, 'volume_id': 'a26887c6-c47b-4654-abb5-dfadf7d3f803',
                'instance_uuid': server_id, 'source_type': 'volume',
                'destination_type': 'volume', 'device_name': '/dev/sdd'}),
                fake_block_device.FakeDbBlockDeviceDict(
                {'id': 2, 'volume_id': 'a26887c6-c47b-4654-abb5-dfadf7d3f804',
                'instance_uuid': server_id, 'source_type': 'volume',
                'destination_type': 'volume', 'device_name': '/dev/sdc'})
            ]
            return bdms

        self.stubs.Set(db, 'block_device_mapping_get_all_by_instance',
                       fake_bdms_get_all_by_instance)

    def _stub_compute_api_get(self):

        def fake_compute_api_get(self, context, instance_id,
                                 want_objects=False, expected_attrs=None):
            if want_objects:
                return fake_instance.fake_instance_obj(
                        context, **{'uuid': instance_id})
            else:
                return {'uuid': instance_id}

        self.stubs.Set(compute_api.API, 'get', fake_compute_api_get)


class VolumeAttachmentsSampleJsonTest(VolumeAttachmentsSampleBase):
    extension_name = "os-volumes"

    def test_attach_volume_to_server(self):
        self.stubs.Set(cinder.API, 'get', fakes.stub_volume_get)
        self.stubs.Set(cinder.API, 'check_attach', lambda *a, **k: None)
        self.stubs.Set(cinder.API, 'reserve_volume', lambda *a, **k: None)
        device_name = '/dev/vdd'
        bdm = objects.BlockDeviceMapping()
        bdm['device_name'] = device_name
        self.stubs.Set(compute_manager.ComputeManager,
                       "reserve_block_device_name",
                       lambda *a, **k: bdm)
        self.stubs.Set(compute_manager.ComputeManager,
                       'attach_volume',
                       lambda *a, **k: None)
        self.stubs.Set(objects.BlockDeviceMapping, 'get_by_volume_id',
                       classmethod(lambda *a, **k: None))

        volume = fakes.stub_volume_get(None, context.get_admin_context(),
                                       'a26887c6-c47b-4654-abb5-dfadf7d3f803')
        subs = {
            'volume_id': volume['id'],
            'device': device_name
        }
        server_id = self._post_server()
        response = self._do_post('servers/%s/os-volume_attachments'
                                 % server_id,
                                 'attach-volume-to-server-req', subs)

        subs.update(self._get_regexes())
        self._verify_response('attach-volume-to-server-resp', subs,
                              response, 200)

    def test_list_volume_attachments(self):
        server_id = self._post_server()

        self._stub_db_bdms_get_all_by_instance(server_id)

        response = self._do_get('servers/%s/os-volume_attachments'
                                % server_id)
        subs = self._get_regexes()
        self._verify_response('list-volume-attachments-resp', subs,
                              response, 200)

    def test_volume_attachment_detail(self):
        server_id = self._post_server()
        attach_id = "a26887c6-c47b-4654-abb5-dfadf7d3f803"
        self._stub_db_bdms_get_all_by_instance(server_id)
        self._stub_compute_api_get()
        response = self._do_get('servers/%s/os-volume_attachments/%s'
                                % (server_id, attach_id))
        subs = self._get_regexes()
        self._verify_response('volume-attachment-detail-resp', subs,
                              response, 200)

    def test_volume_attachment_delete(self):
        server_id = self._post_server()
        attach_id = "a26887c6-c47b-4654-abb5-dfadf7d3f803"
        self._stub_db_bdms_get_all_by_instance(server_id)
        self._stub_compute_api_get()
        self.stubs.Set(cinder.API, 'get', fakes.stub_volume_get)
        self.stubs.Set(compute_api.API, 'detach_volume', lambda *a, **k: None)
        response = self._do_delete('servers/%s/os-volume_attachments/%s'
                                   % (server_id, attach_id))
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, '')

    def test_volume_attachment_update(self):
        self.stubs.Set(cinder.API, 'get', fakes.stub_volume_get)
        subs = {
            'volume_id': 'a26887c6-c47b-4654-abb5-dfadf7d3f805'
        }
        server_id = self._post_server()
        attach_id = 'a26887c6-c47b-4654-abb5-dfadf7d3f803'
        self._stub_db_bdms_get_all_by_instance(server_id)
        self._stub_compute_api_get()
        self.stubs.Set(cinder.API, 'get', fakes.stub_volume_get)
        self.stubs.Set(compute_api.API, 'swap_volume', lambda *a, **k: None)
        response = self._do_put('servers/%s/os-volume_attachments/%s'
                                % (server_id, attach_id),
                                'update-volume-req',
                                subs)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, '')
