# -*- coding: utf-8 -*-
# © 2021 Afonso Carvalho, Netcom

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    sigla = fields.Char()
    diretor = fields.Char()
    diretor_formacao = fields.Char()
    secretaria = fields.Char()
    secretaria_formacao = fields.Char()

    @api.onchange('sigla')
    def set_caps_sigla(self):
        if self.sigla:
            val = str(self.sigla)
            self.sigla = val.upper()

    _sql_constraints = [
        ('sigla_unidade_uniq', 'unique (sigla)',
         'Esta Sigla já está em uso por outra unidade!')
    ]