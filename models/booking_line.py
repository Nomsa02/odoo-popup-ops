from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PopupOpsBookingLine(models.Model):
    _name = "popup.ops.booking.line"
    _description = "Event Equipment or Service Line"
    _order = "id"

    booking_id = fields.Many2one(
        "popup.ops.booking", string="Booking", required=True,
        ondelete="cascade", index=True,
    )
    product_id = fields.Many2one(
        "product.product", string="Equipment / Service", required=True,
        domain="[('sale_ok', '=', True)]",
    )
    quantity = fields.Float(default=1.0, required=True)
    price_unit = fields.Float(string="Estimated Unit Price", digits="Product Price")
    currency_id = fields.Many2one(
        "res.currency", related="booking_id.currency_id", store=True,
    )
    subtotal = fields.Monetary(
        compute="_compute_subtotal", store=True, currency_field="currency_id",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            # An editable starting estimate, not a finalized Odoo rental rate.
            self.price_unit = self.product_id.lst_price

    @api.depends("quantity", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.price_unit

    @api.constrains("quantity", "price_unit")
    def _check_positive_values(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_("Equipment/service quantity must be positive."))
            if line.price_unit < 0:
                raise ValidationError(_("Estimated unit price cannot be negative."))
