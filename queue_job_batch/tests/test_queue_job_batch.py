# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common
from odoo.tools import mute_logger

from odoo.addons.mail.tools.discuss import Store


class TestQueueJobBatchStoreData(common.TransactionCase):
    def test_init_store_data_sets_batch_globals(self):
        batch_group = self.env.ref("queue_job_batch.group_queue_job_batch_user")
        self.env.user.write({"group_ids": [(4, batch_group.id)]})
        self.env["queue.job.batch"].sudo().create(
            {
                "name": "Batch",
                "user_id": self.env.user.id,
                "company_id": self.env.company.id,
                "is_read": False,
            }
        )

        store = Store()
        self.env["res.users"]._init_store_data(store)
        store_data = store.get_result()["Store"]

        self.assertTrue(store_data["hasQueueJobBatchUserGroup"])
        self.assertEqual(store_data["queueJobBatchCounter"], 1)
        self.assertIn("queueJobBatchCounterBusId", store_data)


class TestQueueJobBatchCreatePrivate(common.HttpCase):
    def test_queue_job_create_stays_private(self):
        self.authenticate("admin", "admin")
        with self.assertRaises(common.JsonRpcException) as cm, mute_logger("odoo.http"):
            self.make_jsonrpc_request(
                "/web/dataset/call_kw",
                params={
                    "model": "queue.job",
                    "method": "create",
                    "args": [],
                    "kwargs": {
                        "method_name": "write",
                        "model_name": "res.partner",
                        "uuid": "test",
                    },
                },
            )
        self.assertEqual("odoo.exceptions.AccessError", str(cm.exception))
