from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_instructor = fields.Boolean(string="Is instructor", default=False)

    session_ids = fields.Many2many(
        comodel_name='openacademy.session',
        string='Sessions',
    )

    instructed_session_ids = fields.One2many(
        comodel_name='openacademy.session',
        inverse_name='instructor_id',
        string='Sessions',
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self._get_company(),
        readonly=True,
    )

    def write(self, vals):
        if 'is_instructor' in vals:
            if vals.get('is_instructor'):
                tag_teacher = self.env.ref('openacademy.partner_tag_teacher')
                vals['category_id'] = tag_teacher
            else:
                vals['category_id'] = False
        res = super(ResPartner, self).write(vals)
        return res

    @api.model_create_multi
    def create(self, vals):
        instructor = super(ResPartner, self).create(vals)
        instructor.update_instructor_tag()
        return instructor

    def update_instructor_tag(self):
        for instructor in self:
            if instructor.is_instructor:
                tag_teacher = self.env.ref('openacademy.partner_tag_teacher')
                instructor.category_id = tag_teacher

    def _get_company(self):
        return self.env.company.id
