from odoo import _, api, fields, models
from odoo.exceptions import UserError

class BusinessType(models.Model):
    _name = 'business.type'
    _description = 'Business Type'
    
    name = fields.Char('Business Name')

class WastewaterType(models.Model):
    _name = 'wastewater.type'
    _description = 'Type Wastewater for Tertiary Treatment'
    
    name = fields.Char('name')

class TransportSurvey(models.Model):
    _name = 'transport.survey'
    _description = 'Transport Survey'
    
    name = fields.Char('name')

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    rab_line_ids = fields.One2many('project.rab', 'crm_id', string='RAB')   
    sale_line_ids = fields.One2many('order.line.crm','crm_id', string='Sale Line Product')
    rab_template_id = fields.Many2one('rab.template', string='RAB Template')
    crm_type = fields.Selection([
        ('crm', 'CRM'),
        ('rab', 'RAB')
    ], string='Crm Type')
    business_type_id = fields.Many2one('business.type', string='Business Type')
    ground_water = fields.Boolean('Ground Water')
    surface_water = fields.Selection([
        ('river', 'River'),
        ('lake', 'Lake or reservoir'),
    ], string='Surface Water')
    seawater = fields.Selection([
        ('intake', 'Open intake'),
        ('beach', 'Beach well'),
    ], string='Seawater')
    waste_water_treatment = fields.Selection([
        ('municipal', 'Municipal'),
        ('domestic', 'Domestic'),
        ('industrial', 'Industrial'),
    ], string='Wastewater for Tertiary Treatment')
    distance_from_rawwater = fields.Char('Distance from Raw Water Source to Treatment Plant')
    elevation_from_rawwater = fields.Char('Elevation from Raw Water Source to Treatment Plant')
    #What are the dimensions of the availabl space for the treatment plant?
    length_treatment_plant = fields.Float('Length')
    width_treatment_plant = fields.Float('Width')
    height_treatment_plant = fields.Float('Height')
    gradient_treatment_plant = fields.Float('Gradient')
    
    wind_load = fields.Char('What is the specified wind load?')
    specific_governmental = fields.Boolean('Are there specific governmental standards')
    specific_material = fields.Boolean('Are there specific materials preferred for construction?')
    any_data_available = fields.Boolean('Are there any data available regarding the soil composition, ground water level, etc.?')
    flange_type = fields.Selection([
        ('din', 'DIN'),
        ('ansi', 'ANSI'),
        ('jis', 'JIS')
    ], string='Which flange types are required?')
    is_seasonal_deviations = fields.Boolean('Are there seasonal deviations within the production process(es)?')
    is_height_limitation = fields.Boolean('Are there height limitation?')
    is_area_limitation = fields.Boolean('Are there area limitations?')
    is_limitation_to_transport_tanks = fields.Boolean('Are there any limitations to transport tanks, orreactors, from GLS  to the customer.')
    transport_id = fields.Many2one('transport.survey', string='Transport by')
    # Electrical Condition On Location

    voltage = fields.Float('What is the available voltage?')
    frequency = fields.Float('What is the available frequency?')
    available_power = fields.Float('What is the available power?')
    power = fields.Float('Distance between power supply and treatment plant')
    source_power = fields.Selection([
        ('pln', 'PLN'),
        ('own', 'Own Power Plant')
    ], string='Source of power supply')

    # Description of the Area
    description_area = fields.Html('Description of the Area')
    is_attachment = fields.Boolean('Drawings available?')
    attachment_area = fields.Binary('Attachment')

    # Additional Remarks or Documentations (Pictures, Sketches)

    description_remarks = fields.Html('Additional Remarks or Documentations (Pictures, Sketches)')
    attachment_remarks = fields.Binary('Attachment')

    def action_new_quotation(self):
        res = super(CrmLead, self).action_new_quotation()
        if self.sale_line_ids:
            res['context']['default_order_line'] = [(0,0,{
                'product_id': sale.product_id.id,
                'product_uom_qty': sale.product_uom_qty,
                'product_uom': sale.product_uom.id,
                'name' : sale.name,
                'price_unit': sale.price_unit
            }) for sale in self.sale_line_ids]
        return res
    
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

    crm_id = fields.Many2one('crm.lead', string='CRM')
    rab_template_id = fields.Many2one('rab.template', string='RAB Template')
    # project_id = fields.Many2one('project.project', string='Project')
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer('Sequence')

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
    margin = fields.Float('Margin',compute='_compute_price')
    margin_percent = fields.Float( string='Margin Percent')
    price_subtotal = fields.Float(compute='_compute_price', string='Price Subtotal')

    
    @api.depends('margin_percent','price_unit')
    def _compute_price(self):
        for this in self:
            amount = 0
            amount = this.price_unit * this.margin_percent
            this.margin = amount
            this.price_subtotal = this.price_unit + amount



class OrderLineCrm(models.Model):
    _name = 'order.line.crm'
    _description = 'Order Line CRM'

    crm_id = fields.Many2one('crm.lead', string='CRM')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    product_id = fields.Many2one(
        'product.product', string='Product', domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        change_default=True, ondelete='restrict', check_company=True)  # Unrequired company
    
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure', domain="[('category_id', '=', product_uom_category_id)]")

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=10)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)

class RabTemplate(models.Model):
    _name = 'rab.template'
    _description = 'RAB Template'

    name = fields.Char('Name of Template')
    rab_line_ids = fields.One2many('project.rab', 'rab_template_id', string='Rab Line')

    







