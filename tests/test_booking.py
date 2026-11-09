from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestPopUpOpsBooking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Fictional Test Client"})
        cls.product = cls.env["product.product"].create({
            "name": "Demo Tent Rental", "type": "service", "sale_ok": True,
            "list_price": 150.0,
        })

    def _new_booking(self):
        return self.env["popup.ops.booking"].create({
            "partner_id": self.customer.id,
            "event_name": "Sample Corporate Gathering",
            "venue": "Demo Venue",
            "event_date": "2027-05-01 09:00:00",
            "event_end": "2027-05-01 17:00:00",
            "line_ids": [fields.Command.create({
                "product_id": self.product.id,
                "quantity": 2,
                "price_unit": 150.0,
            })],
        })

    def test_booking_sequence_and_total(self):
        booking = self._new_booking()
        self.assertTrue(booking.name.startswith("EVT/"))
        self.assertEqual(booking.estimated_total, 300.0)

    def test_workflow(self):
        booking = self._new_booking()
        booking.action_confirm()
        self.assertEqual(booking.state, "confirmed")
        booking.action_ready()
        self.assertEqual(booking.state, "ready")
        booking.action_complete()
        self.assertEqual(booking.state, "done")
        with self.assertRaises(UserError):
            booking.action_cancel()

    def test_invalid_event_dates(self):
        with self.assertRaises(ValidationError):
            self.env["popup.ops.booking"].create({
                "partner_id": self.customer.id,
                "event_name": "Bad Date Test",
                "venue": "Demo Venue",
                "event_date": "2027-05-02 10:00:00",
                "event_end": "2027-05-02 09:00:00",
            })

    def test_creates_sales_quotation(self):
        booking = self._new_booking()
        booking.action_confirm()
        action = booking.action_create_quotation()
        self.assertEqual(action["res_model"], "sale.order")
        self.assertEqual(booking.sale_order_id.state, "draft")
        self.assertEqual(booking.sale_order_id.partner_id, self.customer)
        self.assertEqual(len(booking.sale_order_id.order_line), 1)
        self.assertEqual(booking.sale_order_id.order_line.product_uom_qty, 2)
        # Reopening must not create a duplicate quotation.
        self.assertEqual(booking.action_create_quotation()["res_id"], booking.sale_order_id.id)
