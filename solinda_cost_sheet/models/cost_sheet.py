from email.policy import default
from odoo import _, api, fields, models

class CostSheet(models.Model):
    _name = 'cost.sheet'
    _description = 'Cost Sheet'
    _inherit = ['portal.mixin','mail.thread', 'mail.activity.mixin']
    
    name = fields.Char('Name',tracking=True)
    crm_id = fields.Many2one('crm.lead', string='CRM',tracking=True,required=True)
    date_document = fields.Date('Request Date',tracking=True,default=fields.Date.today)
    user_id = fields.Many2one('res.users', string='Responsible',default=lambda self:self.env.user.id)
    rab_template_id = fields.Many2one('rab.template', string='RAB Template',tracking=True)
    rab_line_ids = fields.One2many('project.rab', 'cost_sheet_id', string='RAB')  
    note = fields.Text('Term and condition')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submited'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
    ], string='Status',tracking=True, default="draft")
    purchase_id = fields.Many2one('purchase.requisition', string='Purchase')

    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount',store=True)
    total_margin = fields.Float(compute='_compute_total_amount', string='Margin',store=True)
    total_without_margin = fields.Float(compute='_compute_total_amount', string='Price Subtotal',store=True)
    currency_id = fields.Many2one('res.currency', string='currency',default=lambda self:self.env.company.currency_id.id)


    def action_submit(self):
        self.write({'state':'submit'})

    def action_done(self):
        self.write({'state':'done'})
    def action_to_draft(self):
        self.write({'state':'draft'})
    
    # def create_rap(self):
    #     purchase = self.env['purchase.requisition'].create({
    #         'crm_id': self.crm_id.id,
    #         'origin': self.name,
    #         'date_end' : fields.Datetime.today,
    #         'ordering_date' : fields.Date.today,
    #         'schedule_date' : fields.Date.today,
    #         'line_ids': [(0,0,{
    #             'product_id': template.product_id.id,
    #             'product_qty': template.product_qty,
    #             'product_uom_id': template.uom_id.id,
    #             'product_description_variants' : template.name,
    #             'price_unit': template.price_unit
    #         }) for template in self.rab_line_ids]

    #     })
    #     self.write({'purchase_id':purchase.id})
        
    #     return {
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_model": "purchase.requisition",
    #         "res_id": purchase.id
    #     }

    def action_view_crm(self):
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "crm.lead",
            "res_id": self.crm_id.id
        }

    @api.model
    def create(self, vals):
        res = super(CostSheet, self).create(vals)
        res.name = self.env["ir.sequence"].next_by_code("cost.sheet.seq")
        res.crm_id.rab_id = res.id
        return res 
    
    @api.depends('rab_line_ids.price_subtotal','rab_line_ids.margin','rab_line_ids.price_unit')
    def _compute_total_amount(self):
        for this in self:
            this.total_amount = sum(this.rab_line_ids.mapped('price_subtotal'))
            this.total_without_margin = sum(this.rab_line_ids.mapped('price_unit'))
            this.total_margin = sum(this.rab_line_ids.mapped('margin'))

    @api.onchange('rab_template_id')
    def _onchange_rab_template_id(self):
        if self.rab_line_ids:
            self.write({
                'rab_line_ids': [(5,0,0)]
            })
        else:        
            self.write({
                'rab_line_ids': [(0,0,{
                    'name': template.name,
                    'display_type': template.display_type,
                    'sequence': template.sequence,
                    'product_id': template.product_id.id,
                    'product_qty': template.product_qty,
                    'uom_id': template.uom_id.id,
                    'vol_factor': template.vol_factor,
                    'item_factor': template.item_factor,
                    'lab_factor': template.lab_factor,
                    'start_date': template.start_date,
                    'end_date': template.end_date,
                    'no_pos': template.no_pos,
                    'price_unit': template.price_unit,
                    'margin_percent': template.margin_percent
                }) for template in self.rab_template_id.rab_line_ids]
        }) 

# RAB 

class ProjectRab(models.Model):
    _name = 'project.rab'
    _description = 'Project RAB'

    cost_sheet_id = fields.Many2one('cost.sheet', string='Cost Sheet')
    rab_template_id = fields.Many2one('rab.template', string='RAB Template')
    # project_id = fields.Many2one('project.project', string='Project')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer('Sequence')

    product_id = fields.Many2one('product.product', string='Product')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

    name = fields.Char('Description')
    
    product_qty = fields.Float('Quantity',default=1.0)
    uom_id = fields.Many2one('uom.uom', string='UoM')
    vol_factor = fields.Float('Volume Factor')
    item_factor = fields.Float('Item Factor')
    lab_factor = fields.Float('Lab Factor')
    price_unit = fields.Float('Price')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('Finish Date')
    no_pos = fields.Char('No')
    margin = fields.Float('Margin',compute='_compute_price')
    margin_percent = fields.Float( string='Margin Percent')
    price_subtotal = fields.Float(compute='_compute_price', string='Subtotal')

    
    @api.depends('margin_percent','price_unit')
    def _compute_price(self):
        for this in self:
            amount = 0
            amount = this.price_unit * this.margin_percent
            this.margin = amount
            this.price_subtotal = this.price_unit + amount



class RabTemplate(models.Model):
    _name = 'rab.template'
    _description = 'RAB Template'

    name = fields.Char('Name of Template')
    rab_line_ids = fields.One2many('project.rab', 'rab_template_id', string='Rab Line')

    

