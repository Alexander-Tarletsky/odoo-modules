from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_instructor = fields.Boolean(string="Is instructor", default=False)

    session_ids = fields.Many2many(
        comodel_name='openacademy.session',
        string='Openacademy Sessions',
    )

    instructed_session_ids = fields.One2many(
        comodel_name='openacademy.session',
        inverse_name='instructor_id',
        string='Instructed Sessions',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self._get_company(),
        readonly=True,
    )

    def write(self, vals):
        """Override write method to handle instructor tag assignment.
        
        When is_instructor field is updated, automatically assign or remove
        the teacher tag from the partner's category.
        
        Args:
            vals (dict): Values to write to the record.
            
        Returns:
            bool: Result of the parent write method.
        """
        if 'is_instructor' in vals:
            if vals.get('is_instructor'):
                tag_teacher = self.env.ref('openacademy.partner_tag_teacher')
                vals['category_id'] = tag_teacher
            else:
                vals['category_id'] = False
        res = super(ResPartner, self).write(vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """Override create method to handle instructor tag assignment.
        
        Creates partner records and updates instructor tags if needed.
        
        Args:
            vals_list (list): List of dictionaries with values for new records.
            
        Returns:
            res.partner: Created partner records.
        """
        instructor = super(ResPartner, self).create(vals_list)
        instructor.update_instructor_tag()
        return instructor

    def update_instructor_tag(self):
        """Update instructor tag for partners marked as instructors.
        
        Assigns the teacher tag to partners who are marked as instructors.
        """
        for instructor in self:
            if instructor.is_instructor:
                tag_teacher = self.env.ref('openacademy.partner_tag_teacher')
                instructor.category_id = tag_teacher

    def _get_company(self):
        """Get the current company ID from the environment.
        
        Returns:
            int: The current company ID.
        """
        return self.env.company.id
