from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PopupOpsBooking(models.Model):
    """An independent event booking; not tied to any employer's business logic."""

    _name = "popup.ops.booking"
    _description = "Event Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "event_date desc, id desc"
    _check_company_auto = True

    name = fields.Char(
        string="Booking Number", required=True, copy=False, readonly=True,
        default=lambda self: _("New"), tracking=True,
    )
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True,
    )
    company_id = fields.Many2one(
        "res.company", required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", store=True,
    )
    event_name = fields.Char(string="Event Name", required=True, tracking=True)
    event_type = fields.Selection([
        ("wedding", "Wedding"),
        ("corporate", "Corporate Event"),
        ("birthday", "Birthday / Celebration"),
        ("market", "Market / Exhibition"),
        ("other", "Other"),
    ], required=True, default="corporate")
    venue = fields.Char(required=True)
    event_date = fields.Datetime(string="Event Start", required=True, tracking=True)
    event_end = fields.Datetime(string="Event End")
    guest_count = fields.Integer(default=0)
    coordinator_id = fields.Many2one(
        "res.users", string="Coordinator", default=lambda self: self.env.user,
    )
    notes = fields.Text()
    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("ready", "Ready for Setup"),
        ("done", "Completed"),
        ("cancel", "Cancelled"),
    ], default="draft", required=True, tracking=True, copy=False)
    line_ids = fields.One2many(
        "popup.ops.booking.line", "booking_id", string="Equipment & Services",
        copy=True,
    )
    estimated_total = fields.Monetary(
        string="Estimated Total", compute="_compute_estimated_total",
        store=True, currency_field="currency_id",
    )
    sale_order_id = fields.Many2one(
        "sale.order", string="Sales Quotation", readonly=True,
        copy=False, check_company=True,
    )

    @api.depends("line_ids.subtotal")
    def _compute_estimated_total(self):
        for booking in self:
            booking.estimated_total = sum(booking.line_ids.mapped("subtotal"))

    @api.constrains("event_date", "event_end", "guest_count")
    def _check_event_details(self):
        for booking in self:
            if booking.event_end and booking.event_date and booking.event_end <= booking.event_date:
                raise ValidationError(_("Event end must be after event start."))
            if booking.guest_count < 0:
                raise ValidationError(_("Guest count cannot be negative."))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "popup.ops.booking"
                ) or _("New")
        return super().create(vals_list)

    def action_confirm(self):
        for booking in self:
            if booking.state != "draft":
                raise UserError(_("Only draft bookings can be confirmed."))
            if not booking.line_ids:
                raise UserError(_("Add at least one equipment or service line first."))
        self.write({"state": "confirmed"})
        return True

    def action_ready(self):
        for booking in self:
            if booking.state != "confirmed":
                raise UserError(_("Only confirmed bookings can be marked ready."))
        self.write({"state": "ready"})
        return True

    def action_complete(self):
        for booking in self:
            if booking.state != "ready":
                raise UserError(_("Only ready bookings can be completed."))
        self.write({"state": "done"})
        return True

    def action_cancel(self):
        for booking in self:
            if booking.state == "done":
                raise UserError(_("Completed bookings cannot be cancelled."))
        self.write({"state": "cancel"})
        return True

    def action_reset_draft(self):
        for booking in self:
            if booking.state != "cancel":
                raise UserError(_("Only cancelled bookings can return to draft."))
        self.write({"state": "draft"})
        return True

    def action_create_quotation(self):
        """Create a draft Sales quotation with the booking's estimated lines.

        The current user needs Sales access. No sudo is used to bypass permissions.
        This intentionally does NOT reserve stock or post invoices.
        """
        self.ensure_one()
        if self.state not in ("confirmed", "ready"):
            raise UserError(_("Confirm the booking before creating a quotation."))
        if self.sale_order_id:
            return self.action_open_quotation()
        if not self.line_ids:
            raise UserError(_("Add equipment or services before creating a quotation."))

        # Odoo enforces the user's ordinary Sales permissions here.
        sale_order = self.env["sale.order"].create({
            "partner_id": self.partner_id.id,
            "company_id": self.company_id.id,
            "origin": f"{self.name} - {self.event_name}",
            "order_line": [
                fields.Command.create({
                    "product_id": line.product_id.id,
                    "name": line.product_id.get_product_multiline_description_sale()
                    or line.product_id.display_name,
                    "product_uom_qty": line.quantity,
                    "product_uom": line.product_id.uom_id.id,
                    "price_unit": line.price_unit,
                })
                for line in self.line_ids
            ],
        })
        self.sale_order_id = sale_order
        return self.action_open_quotation()

    def action_open_quotation(self):
        self.ensure_one()
        if not self.sale_order_id:
            raise UserError(_("This booking has no Sales quotation yet."))
        return {
            "type": "ir.actions.act_window",
            "name": _("Sales Quotation"),
            "res_model": "sale.order",
            "view_mode": "form",
            "res_id": self.sale_order_id.id,
            "target": "current",
        }
