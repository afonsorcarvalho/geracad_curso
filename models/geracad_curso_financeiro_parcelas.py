# -*- coding: utf-8 -*-

from re import M
from odoo import models, fields, api, _
from datetime import date, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, misc

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

    type_curso =   fields.Many2one(
        string="Tipo do Curso",
        related="curso_matricula_id.curso_id.type_curso",
        readonly=True,
        store=True,

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

    unidade_curso_turma_id = fields.Many2one(
        related = 'curso_matricula_id.curso_turma_id.company_id',
        string='Unidade do Aluno',
        readonly=True,
        store=True,
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
    numero_parcela = fields.Integer("Parcela",group_operator=False)
    valor = fields.Monetary(string='Valor', required=True, track_visibility='true')
    valor_pago = fields.Monetary(string='Valor Pago', required=True, default=0, track_visibility='true')
    esta_pago = fields.Boolean("Pago", default=0, track_visibility='true')
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
        ('vigente', 'A receber'),
        ('cancelado', 'Cancelado'),
        ('recebido', 'Recebido'),
        ('suspenso', 'Suspenso'),
    ], string="Status", default="draft", track_visibility='true')

    active = fields.Boolean(default = True)


    def _compute_codigo_parcela(self):
        _logger.info("gerando codigo parcela")
        self.name = self.contrato_id.name + ""
    
    
    def action_ajeita_status_parcela(self):
        
        _logger.info("ajeitando estatus da parcela")
        for rec in self:
            if rec.esta_pago and (rec.state == 'vigente' or rec.state == 'draft') :
                rec.state = 'recebido'
    #################################
    # 
    # USADO NA IMPRESSAO            

    def get_date_str(self):
        data_pagamento = self.data_pagamento
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        try:
            date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(data_pagamento,format="long",locale=locale)
        except:
            date_str = "SEM DATA"
        return   date_str


    
  
    """

            BUTTON ACTIONS

    """

    def action_pagar_parcela(self):
        if self.state == 'recebido' or self.esta_pago:
            raise ValidationError('Parcela já está paga!')
        if self.state == 'suspenso':
            raise ValidationError('Parcela está suspensa. Provavelmente a matrícula do aluno está trancada!')
        if self.state == 'cancelada':
            raise ValidationError('Parcela está cancelada. Não pode ser paga!')

        dummy, act_id = self.env["ir.model.data"].sudo().get_object_reference(
            "geracad_curso", "action_geracad_curso_pagamento_parcela"
        )
        
        vals = self.env["ir.actions.act_window"].sudo().browse(act_id).read()[0]
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
        if self.state != 'recebido' or not self.esta_pago:
            raise ValidationError('A Parcela não foi paga ainda! ')
        if self.state == 'suspenso':
            raise ValidationError('Parcela está suspensa. Provavelmente a matrícula do aluno está trancada!')
        if self.state == 'cancelada':
            raise ValidationError('Parcela está cancelada. Não pode ser paga!')

        _logger.debug("CANCELAR PAGAMENTO DE PARCELA")
        self.write({
            'state': 'recebido',
            'valor_pago': 0,
            'esta_pago' : False,

        })
