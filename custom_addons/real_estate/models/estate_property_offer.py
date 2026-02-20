from odoo import api, models, fields, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class PropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
    _order = "price desc"

    # SQL Constraints
    _sql_constraints = [
        ("check_price", "CHECK(price > 0)", "The price offer must be positive.")
    ]

    # ---------- Fields ----------
    price = fields.Float(string="Price", required=True)
    status = fields.Selection(
        string="Status",
        selection=[("accepted", "Accepted"), ("refused", "Refused")],
        copy=False,
    )
    partner_id = fields.Many2one("res.partner", string="Buyer", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(
        related="property_id.property_type_id", store=True, string="Property Type"
    )
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True,
    )

    # ---------- Computed Methods ----------
    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            record.date_deadline = fields.Date.today() + relativedelta(
                days=record.validity
            )

    def _inverse_date_deadline(self):
        for record in self:
            record.validity = (record.date_deadline - fields.Date.today()).days

    # ---------- Button Methods ----------
    def action_accept(self):
        self.ensure_one()
        # Controlla se esiste già un'offerta accettata per la proprietà
        if "accepted" in self.property_id.offer_ids.mapped("status"):
            raise UserError(_("This property has already been sold!"))

        self.status = "accepted"
        self.property_id.selling_price = self.price
        self.property_id.buyer = self.partner_id

    def action_refuse(self):
        self.ensure_one()
        self.status = "refused"
