from odoo import _, models, fields, api


class PropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real Estate Property Type"
    _order = "sequence, name"
    _sql_constraints = [
        ("unique_type_name", "UNIQUE(name)", "Property types shoulde be unique")
    ]

    sequence = fields.Integer(default=1)
    name = fields.Char(string="Property Type", required=True)
    property_ids = fields.One2many(
        "estate.property", "property_type_id", string="Properties"
    )
    offer_ids = fields.One2many(
        "estate.property.offer", "property_type_id", string="Offers"
    )
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    # STAT BUTTON

    def action_open_offer_ids(self):
        return {
            "name": _("Property Offers"),
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "estate.property.offer",
            "target": "current",
            "domain": [("property_type_id", "=", self.id)],
            "context": {"default_property_type_id": self.id},
        }

    #
