# -*- coding: utf-8 -*-

from odoo import models, fields

class IrUiView(models.Model):
    """
    Extensão do modelo ir.ui.view para adicionar o novo tipo de view 'horario_semanal'
    """
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[
        ('horario_semanal', "Horário Semanal")
    ], ondelete={'horario_semanal': 'cascade'})

class ActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('horario_semanal', "Horário Semanal")],ondelete={'horario_semanal': 'cascade'})

