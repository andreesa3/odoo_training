from odoo import api, models, fields, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate"
    _order = "id desc"

    # Fields
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Available From",
        default=fields.Date.today() + relativedelta(months=3),
        copy=False,
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False,
    )
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("new", "New"),
            ("offer_rec", "Offer Received"),
            ("offer_acc", "Offer Accepted"),
            ("sold", "Sold"),
            ("canc", "Cancelled"),
        ],
        default="new",
        required=True,
        copy=False,
    )
    active = fields.Boolean(string="Active", default=True)

    # Relational data
    property_type_id = fields.Many2one(
        "estate.property.type", string="Property Type", copy=False
    )
    buyer = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    # Computed fields
    total_area = fields.Float(compute="_compute_total")
    best_price = fields.Float(compute="_compute_best")

    # Methods
    @api.depends("living_area", "garden_area")
    def _compute_total(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best(self):
        for record in self:
            prices = record.offer_ids.mapped("price")
            record.best_price = max(prices) if prices else 0.0
            if record.best_price:
                record.state = "offer_rec"

    @api.onchange("garden")
    def _onchange_garden(self):
        for record in self:
            if record.garden:
                record.garden_area = 10
                record.garden_orientation = "north"
            else:
                record.garden_area = 0
                record.garden_orientation = False

    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        for record in self:
            if record.date_availability < fields.Date.today():
                return {
                    "warning": {
                        "title": ("Warning"),
                        "message": ("Availability Date is et in the past"),
                    }
                }

    # Buttons Method
    def property_sold(self):
        self.ensure_one()
        if self.state == "canc":
            raise UserError(_("Cancelled properties cannot be sold"))
        self.state = "sold"

    def property_cancelled(self):
        self.ensure_one()
        if self.state == "sold":
            raise UserError(_("Sold properties cannot be cancelled"))
        self.state = "canc"

    # Constraints
    @api.constrains("selling_price", "expected_price")
    def _check_selling_price(self):
        for record in self:
            if not record.selling_price:
                continue
            # Controllo se selling_price < 90% di expected_price
            if (
                float_compare(
                    record.selling_price,
                    record.expected_price * 0.9,
                    precision_digits=2,
                )
                == -1
            ):
                raise ValidationError(
                    _(
                        "Selling price should not be lower than 90% of the expected price."
                    )
                )

    @api.constrains("expected_price")
    def _check_selling_price(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError(_("Expected price should be positive!"))
