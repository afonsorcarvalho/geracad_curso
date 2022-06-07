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
    _order = "id desc"

    
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
    curso_turma_codigo = fields.Char(
        related = 'curso_matricula_id.curso_turma_codigo',
        string='Curso Turma',
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
    valor = fields.Monetary(string='Valor', required=True, track_visibility='true')
    valor_pago = fields.Monetary(string='Valor Pago', required=True, default=0, track_visibility='true')
    esta_pago = fields.Boolean("Pago", default=0)
    juros = fields.Float("Juros")
    multa = fields.Float("Multa")
    desconto = fields.Float("Desconto")
    observacao = fields.Text("Anotações")
    

    forma_de_pagamento = fields.Selection(
        string = 'Forma de Pagamento',
        selection = [('dinheiro', 'Dinheiro'), 
            ('boleto', 'Boleto'),
            ('cheque', 'Cheque'),
            ('emp_cobranca', 'Empresa de Cobrança'), 
            ('debito', 'Cartão Débito'), 
            ('credito', 'Cartão Crédito'), 
            ('deposito', 'Depósito Bancário'),
            ('tribunal','Tribunal'), 
            
            ],
        required=True,
        track_visibility='true'

    )
    


    sacado = fields.Many2one('res.partner',string="Sacado")
    sacado_cpf = fields.Char(string="CPF", related='sacado.l10n_br_cnpj_cpf', store=True)
  
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('vigente', 'Vigente'),
        ('cancelado', 'Cancelado'),
        ('recebido', 'Recebido'),
        ('suspenso', 'Suspenso'),
    ], string="Status", default="draft", track_visibility='true')

    active = fields.Boolean(default = True)


    def _compute_codigo_parcela(self):
        _logger.info("gerando codigo parcela")
        self.name = self.contrato_id.name + ""
    

    
  
    """

            BUTTON ACTIONS

    """

    def action_pagar_parcela(self):
        if self.state == 'recebido' or self.esta_pago:
            raise ValidationError('Parcela já está paga!')

        dummy, act_id = self.env["ir.model.data"].get_object_reference(
            "geracad_curso", "action_geracad_curso_pagamento_parcela"
        )
        
        vals = self.env["ir.actions.act_window"].browse(act_id).read()[0]
        vals["context"] = {
            "default_valor_devido": self.valor,
            "default_valor_pago": self.valor,
            "default_company_id": self.company_id.id,
            
            "default_aluno_id": self.aluno_id.id,
           
            "default_parcela_id": self.id,
            "default_forma_de_pagamento": self.forma_de_pagamento,
            "default_comunication": self.observacao,
        }
        return vals
    
    def action_cancelar_pagamento_parcela(self):
        _logger.debug("CANCELAR PAGAMENTO DE PARCELA")
        self.write({
            'state': 'recebido',
            'valor_pago': 0,
            'esta_pago' : False,

        })
