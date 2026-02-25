from odoo import models, fields


class EstateChatter(models.Model):
    _name = "estate.chatter"
    _inherit = ["mail.thread", "mail.activity.mixin"]
