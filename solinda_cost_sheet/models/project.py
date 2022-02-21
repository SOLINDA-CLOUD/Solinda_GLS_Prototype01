from odoo import _, api, fields, models

class ProjectProject(models.Model):
    _inherit = 'project.project'


    rab_line_ids = fields.One2many('project.rab', 'project_id', string='RAB')    

class ProjectRab(models.Model):
    _name = 'project.rab'
    _description = 'Project RAB'

    project_id = fields.Many2one('project.project', string='Project')
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char('Description')
    product_qty = fields.Float('Product Qty')
    uom_id = fields.Many2one('uom.uom', string='UoM')
    vol_factor = fields.Float('Volume Factor')
    item_factor = fields.Float('Item Factor')
    lab_factor = fields.Float('Lab Factor')
    price_unit = fields.Float('Price')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('Finish Date')
    no_pos = fields.Char('No')



    