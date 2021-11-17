# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta
from re import M
from odoo import models, fields, api, _
from datetime import date,timedelta

from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoContrato(models.Model):
    _name = "geracad.curso.contrato"
    _description = "Contratos de Cursos"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código",
        compute='_compute_codigo_contrato' )
    
    @api.depends('curso_matricula_id')
    def _compute_codigo_contrato(self):
        for record in self:
            record.name = record.curso_matricula_id.name
    
    
    
    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, default=lambda self: self.env.company
    )
    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string='Matricula',
        required=True
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
   
    data_inicio = fields.Date(
        string='Data Início',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )
    data_encerramento = fields.Date(
        string='Data Encerramento',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )
    qtd_parcelas = fields.Integer(string='Qtd. parcelas',required=True)
    valor_parcelas = fields.Monetary(string='Valor', required=True)
    juros = fields.Float("Juros")
    multa = fields.Float("Multa")
    desconto = fields.Float("Desconto")
    data_vencimento_parcelas = fields.Date("Vencimento parcelas", required=True)
    parcelas_contrato_ids = fields.One2many('geracad.curso.financeiro.parcelas', 'contrato_id')
    valor_total = fields.Float("Valor Total", compute="_compute_valor_total_contrato")
    valor_total_pago = fields.Float("Valor Total Pago", compute="_compute_valor_total_pago_contrato")
    valor_a_pagar = fields.Float("Valor Total a Pagar", compute="_compute_valor_total_a_pagar_contrato")

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
    


    sacado = fields.Many2one('res.partner',string="Sacado", required=True)
    sacado_cpf = fields.Char(string="CPF", related='sacado.l10n_br_cnpj_cpf', store=True)
  
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('vigente', 'Vigente'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ], string="Status", default="draft", track_visibility='onchange')

    active = fields.Boolean(default = True)
    
    @api.depends('parcelas_contrato_ids')  
    def _compute_valor_total_contrato(self):
        _logger.info("CALCULANDO VALOR TOTAL DO CONTRATO")
        _logger.debug(self.parcelas_contrato_ids)
      
        soma = 0
        for parcela in self.parcelas_contrato_ids:
            _logger.debug(parcela)
            _logger.info(parcela.valor)
            soma += parcela.valor
        self.valor_total = soma

    @api.depends('parcelas_contrato_ids')  
    def _compute_valor_total_a_pagar_contrato(self):
        _logger.info("CALCULANDO TOTAL A PAGAR DO CONTRATO")
        self.valor_a_pagar = self.valor_total - self.valor_total_pago

    @api.depends('parcelas_contrato_ids')  
    def _compute_valor_total_pago_contrato(self):
        _logger.info("CALCULANDO TOTAL PAGO DO CONTRATO")
        parcelas = self.env['geracad.curso.financeiro.parcelas'].search([('contrato_id', '=',self.id)])
        
        soma = 0
        for parcela in parcelas:
            soma += parcela.valor_pago
        self.valor_total_pago = soma

    def _gera_parcelas_financeiro(self, qtd_parcelas, valor_parcelas):
        _logger.info("GERANDO PARCELAS FINANCEIRO")
        
        for number in range(qtd_parcelas):
            _logger.info(self.data_vencimento_parcelas + relativedelta(months=(number)))
            self.write({
                'parcelas_contrato_ids':[(0,0,{
                    'name': self.name + "-"+ str(number),
                    'curso_matricula_id': self.curso_matricula_id.id,
                    'contrato_id': self.id,
                    'data_vencimento': self.data_vencimento_parcelas + relativedelta(months=(number)),
                    'numero_parcela': number+1,
                    'valor': valor_parcelas,
                    'juros': self.juros,
                    'desconto': self.desconto,
                    'multa': self.multa,
                    'forma_de_pagamento': self.forma_de_pagamento,
                    'sacado': self.sacado.id,
                    


                
                })]
            })


    
    def _cancela_parcelas_financeiro(self):
        _logger.info("CANCELANDO PARCELAS FINANCEIRO")
    
    def _verifica_parcelas_abertas_financeiro(self):
        _logger.info("VERFICANDO PARCELAS EM ABERTO")
        return False
    
    """

            BUTTON ACTIONS

    """

    def action_confirma_contrato(self):
       
        self.curso_matricula_id.write({
            'contrato_gerado' : 1
        })
        self.write({
            'state': 'vigente',
           })
        
    def action_gera_parcelas(self):
        self._gera_parcelas_financeiro(self.qtd_parcelas,self.valor_parcelas)
        
        
        
    def action_cancela_contrato(self):
        self._cancela_parcelas_financeiro()
        self.curso_matricula_id.write({
            'contrato_gerado' : 0
        })
        self.write({
            'state': 'vigente',
           })
    def action_finaliza_contrato(self):
        if self._verifica_parcelas_abertas_financeiro():
            self.write({
                'state': 'finalizado',
            })
        else:
            raise ValidationError('Contrato com parcelas em aberto. Não pode ser finalizado!')

            


    # def action_encerrar_matricula(self):
    #     self.write({
    #         'state': 'encerrada',
    #         'matricula_aberta': False,
    #         })
    
    # def action_cancelar_matricula(self):
    #     self.write({
    #         'state': 'cancelada',
    #         'matricula_aberta': False,
    #         })

    # def action_abrir_matricula(self):
    #     self.write({
    #         'state': 'aberta',
    #         'matricula_aberta': True,
    #         })
    
    # def action_go_matriculas(self):

    #     _logger.info("action open matriculas")
        
    #     return {
    #         'name': _('Matriculados'),
    #         'type': 'ir.actions.act_window',
    #         'target':'current',
    #         'view_mode': 'tree,form',
    #         'res_model': 'geracad.curso.matricula',
    #         'domain': [('curso_turma_id', '=', self.id)],
    #     }
        


        

    
       