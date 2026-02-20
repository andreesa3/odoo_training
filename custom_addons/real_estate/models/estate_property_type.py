from odoo import models, fields


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
