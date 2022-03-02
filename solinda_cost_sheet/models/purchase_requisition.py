from odoo import _, api, fields, models

class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    crm_id = fields.Many2one('crm.lead', string='CRM')

    type = fields.Selection([
        ('rap', 'RAP')
    ], string='type')    