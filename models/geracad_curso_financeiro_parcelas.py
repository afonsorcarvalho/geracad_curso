# -*- coding: utf-8 -*-

from re import M
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoFinanceiroParcelas(models.Model):
    _name = "geracad.curso.financeiro.parcelas"
    _description = "Parcelas do curso"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código" )
    
   
    
    
    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, default=lambda self: self.env.company
    )
    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string='Matricula',
        required=True
        )
    contrato_id = fields.Many2one(
        'geracad.curso.contrato',
        string='Contrato',
        required=False
        )
    aluno_id = fields.Many2one(
        
        related = 'curso_matricula_id.aluno_id',
        string='Nome do Aluno',
        readonly=True,
        store=True,
        )   
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string="Company Currency", readonly=True)

    curso_nome = fields.Char(
        related = 'curso_matricula_id.curso_nome',
        string='Curso',
        readonly=True,
        store=True
        )
   
    data_vencimento = fields.Date(
        string='Data Vencimento',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    data_pagamento = fields.Date(
        string='Data Pagamento',
        
        track_visibility='true'
    )
    numero_parcela = fields.Integer("Parcela")
    valor = fields.Monetary(string='Valor', required=True)
    valor_pago = fields.Monetary(string='Valor Pago', required=True, default=0)
    esta_pago = fields.Boolean("Pago", default=0)
    juros = fields.Float("Juros")
    multa = fields.Float("Multa")
    desconto = fields.Float("Desconto")
    

    forma_de_pagamento = fields.Selection(
        string = 'Forma de Pagamento',
        selection = [('dinheiro', 'Dinheiro'), 
            ('boleto', 'Boleto'),
            ('cheque', 'Cheque'),
            ('emp_cobranca', 'Empresa de Cobrança'), 
            ('debito', 'Cartão Débito'), 
            ('credito', 'Cartão Crédito'), 
            ('deposito', 'Depósito Bancário'), 
            
            ],
        required=True

    )
    


    sacado = fields.Many2one('res.partner',string="Sacado")
    sacado_cpf = fields.Char(string="CPF", related='sacado.l10n_br_cnpj_cpf', store=True)
  
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('vigente', 'Vigente'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
        ('suspenso', 'Suspenso'),
    ], string="Status", default="draft", track_visibility='true')

    active = fields.Boolean(default = True)


    def _compute_codigo_parcela(self):
        _logger.info("gerando codigo parcela")
        self.name = self.contrato_id.name + ""

   
    
  
    """

            BUTTON ACTIONS

    """

    

            


        

    
       