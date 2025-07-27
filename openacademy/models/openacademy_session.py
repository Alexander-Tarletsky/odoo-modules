from datetime import timedelta, date
from odoo import fields, models, api, exceptions, _


class Session(models.Model):
    _name = 'openacademy.session'
    _description = "Open Academy Sessions"
    _order = 'course_id'
    _rec_name = 'course_id'
    _check_company_auto = True

    active = fields.Boolean(default=True)

    color = fields.Integer()

    start_date = fields.Date(
        string='Start Date',
        default=lambda self: fields.datetime.now(),
    )

    seats = fields.Integer(string='Seats', required=True, default=10)
    duration = fields.Integer(string='Duration of days')

    course_id = fields.Many2one(
        comodel_name='openacademy.course',
        string='Course',
        ondelete='cascade',
        required=True,
    )

    instructor_id = fields.Many2one(
        comodel_name='res.partner',
        string='Instructor',
        ondelete='cascade',
        domain=[('is_instructor', '=', True), ('is_company', '=', False)],
        required=True,
        default=lambda self: self.env.uid,   # _uid
        check_company=True,
    )

    attendee_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Attendees',
    )

    number_attendees = fields.Integer(
        string='Number of attendees',
        compute='_compute_number_attendees',
        store=True,
    )

    taken_percentage = fields.Float(
        string='Occipied places',
        compute='_compute_taken_percentage',
        store=True,
    )

    end_date = fields.Date(
        string='End Date',
        compute='_compute_end_date',
        inverse='_inverse_end_date',
        store=True,
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self._get_company().id,
        readonly=True,
    )

    @api.depends('seats', 'attendee_ids',)
    def _compute_taken_percentage(self):
        for session in self:
            if len(session.attendee_ids) > 0:
                occupancy = len(session.attendee_ids) / session.seats * 100
                session.taken_percentage = occupancy
            else:
                session.taken_percentage = 0

    @api.depends('start_date', 'duration',)
    def _compute_end_date(self):
        for session in self:
            session.end_date = session.start_date + timedelta(days=session.duration)

    def _inverse_end_date(self):
        for session in self:
            duration = session.end_date - session.start_date
            session.duration = duration.days

    @api.depends('attendee_ids')
    def _compute_number_attendees(self):
        for record in self:
            record.number_attendees = len(record.attendee_ids)

    @api.onchange('seats', 'attendee_ids')
    def _check_seats(self):
        """
        Do not allowed to set the number of seats less than the number participants
        """
        for record in self:
            if record.seats < len(record.attendee_ids):
                raise exceptions.UserError(
                    _("Number of seats should be more than number of participants")
                )

    @api.onchange('end_date', 'duration', )
    def _check_date(self):
        """
        Do not allowed to set negative session duration
        """
        for session in self:
            duration = session.end_date - session.start_date

            if session.duration < 0 or duration.days < 0:
                raise exceptions.UserError(_("Duration cannot be negative"))

    @api.onchange('attendee_ids')
    def _onchange_attendees(self):
        """If OACompany is closed - display a warning"""
        if not self.env.company.company_is_open:
            return {
                'warning': {
                    'title': _("This company is closed"),
                    'message': _("You cannot change the number of participants in the sessions"),
                }
            }

    @api.constrains('attendee_ids')
    def _check_attendee(self):
        for record in self.attendee_ids:
            if record.is_instructor:
                raise exceptions.ValidationError(
                    _("Error adding session attendee! Instructor cannot be a attendee")
                )

    @api.constrains('instructor_id')
    def _check_instructor(self):
        for record in self.instructor_id:
            if not record.is_instructor:
                raise exceptions.ValidationError(
                    _("Error adding session instructor! This participant is not an instructor")
                )

    def _get_company(self):
        return self.env.company

    def notify_about_start_session(self):
        """
        Send an email notification of the start of a session to each participant
        """
        company = self.env.company
        start_date = date.strftime(date.today() + timedelta(days=1), '%Y-%m-%d')
        starting_sessions = self.search([['start_date', '=', start_date]])

        for session in starting_sessions:
            participants = [s.email for s in session.attendee_ids if s.email]

            if participants:
                context = self.env.context.copy()
                context.update({'session': session, 'participants': ','.join(participants)})

                mail_template = self.env.ref('openacademy.session_start_notification_email')
                mail_template.with_context(context).send_mail(company.id, force_send=True)
