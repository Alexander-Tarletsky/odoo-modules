from odoo import api, fields, models


class Course(models.Model):
    _name = 'openacademy.course'
    _description = "Open Academy Courses"
    _order = 'title'
    _rec_name = 'title'

    active = fields.Boolean(default=True)

    title = fields.Char(string="Title course", required=True,)
    description = fields.Text()

    session_ids = fields.One2many(
        comodel_name='openacademy.session',
        inverse_name='course_id',
        string='Sessions',
        domain=lambda self: [('company_id', '=', self._get_company().id)]
    )

    responsible_id = fields.Many2one(
        comodel_name='res.users',
        string='Responsible',
        ondelete='cascade',
        domain=lambda self: [('company_id', '=', self._get_company().id)]
    )

    state = fields.Selection(
        selection=[
            ('active', 'Active'),
            ('inactive', 'Not Active'),
        ],
        default="active",
        required=True,
        readonly=True,
        copy=False,
    )

    # Replace direct price field with computed field
    price = fields.Monetary(
        string="Price of Course",
        compute='_compute_price',
        inverse='_inverse_price',
        # store=True,
        currency_field='currency_id',
        # readonly=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True,
        company_dependent=True,
        default=lambda self: self._get_company().currency_id.id,
    )

    # Add One2many relationship to course prices
    course_price_ids = fields.One2many(
        comodel_name='openacademy.course.price',
        inverse_name='course_id',
        string='Course Prices by Company',
    )

    _sql_constraints = [
        (
            'title_unique',
            'UNIQUE(title)',
            "The course title must be unique"
        ),
    ]

    # @api.depends('course_price_ids.price')
    @api.depends_context('company')
    def _compute_price(self):
        """Compute price based on company-specific pricing"""
        company = self._get_company()
        for course in self:
            price_record = course.course_price_ids.filtered(
                lambda p: p.company_id == company
            )
            course.price = price_record.price if price_record else 0.0

    def _inverse_price(self):
        """Set price in company-specific pricing record"""
        company = self._get_company()
        for course in self:
            price_record = course.course_price_ids.filtered(
                lambda p: p.company_id == company
            )

            if price_record:
                price_record.price = course.price
            else:
                # Create new price record for this company
                currency_id = course.currency_id.id or self._get_company().currency_id.id
                self.env['openacademy.course.price'].create({
                    'course_id': course.id,
                    'company_id': company.id,
                    'price': course.price,
                    'currency_id': currency_id,
                })

    def move_to_archive(self):
        """
        Deactivate course and remove sessions
        """
        self.ensure_one()
        self.active = False
        self.with_context(active=False).change_state()
        self.session_ids = []

    def restore_from_archive(self):
        """
        Mark course as active
        """
        self.ensure_one()
        self.active = True
        self.with_context(active=True).change_state()

    def change_state(self):
        """
        Change of state field
        """
        if self.env.context.get('active'):
            self.write({'state': 'active'})
        else:
            self.write({'state': 'inactive'})

    def _get_company(self):
        """Get the current company from the environment.

        Returns:
            res.company: The current company record.
        """
        return self.env.company

    def copy(self, default=None):
        """Create a copy of the course with a unique title.

        Args:
            default (dict, optional): Default values for the copy. Defaults to None.

        Returns:
            openacademy.course: The copied course record.
        """
        if not default:
            default = {}
        title = self.title
        list_title = self.search([('title', 'like', str(title) + '%')])

        if list_title:
            title = f'Duplicate of {title} ({len(list_title)})'
        else:
            title = f'Duplicate of {title}'

        default['title'] = title
        new_course = super().copy(default=default)
        return new_course
