from odoo import models, fields

class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Real Estate Property Tag'
    _order = 'name'
    # SQL Constraints
    _sql_constraints = [
        ("unique_tag_name", "UNIQUE(name)", "Tag name should be unique.")
    ]

    name = fields.Char(string="Name", required=True)
    color = fields.Integer("Color")