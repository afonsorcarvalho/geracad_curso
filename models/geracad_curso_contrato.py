# -*- coding: utf-8 -*-
import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from datetime import date,timedelta
from num2words import num2words
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, misc
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoContrato(models.Model):
    """Class method to create a Geracadcad . crt .

    Args:
        models ([type]): [description]
    """
    
    _name = "geracad.curso.contrato"
    _description = "Contratos de Cursos"
#  _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código",
        compute='_compute_codigo_contrato' )
    
    @api.depends('curso_matricula_id')
    def _compute_codigo_contrato(self):
        for record in self:
            record.name = record.curso_matricula_id.name
    
    
    #TODO - Pegar a unidade a mesma da matricula caso tenha sido selecionado a matricula do aluno
    # caso contrario a companhia do poprio usuario
    

    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, default=lambda self: self.env.company
    )
    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string='Matricula',
        required=True
        )
    curso_type = fields.Many2one(
        'geracad.curso.type',
        related='curso_matricula_id.curso_id.type_curso',
       
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
        tracking=True
    )
    data_encerramento = fields.Date(
        string='Data Encerramento',
        default=fields.Date.context_today,
        tracking=True
    )
    qtd_parcelas = fields.Integer(string='Qtd. parcelas',required=True)
    valor_parcelas = fields.Monetary(string='Valor', required=True)
    parcelas_geradas = fields.Boolean(string="Parcelas geradas", default=False)
    juros = fields.Float("Juros")
    multa = fields.Float("Multa")
    desconto = fields.Float("Desconto")
    data_vencimento_parcelas = fields.Date("Vencimento parcelas", required=True)
    parcelas_contrato_ids = fields.One2many('geracad.curso.financeiro.parcelas', 'contrato_id')
    data_assinatura_contrato = fields.Date("Data assinatura", required=True)
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
        ('suspenso', 'Suspenso'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ], string="Status", default="draft", tracking=True)

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
        """Compute the total valor de pagar de contato .
        """
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
            self.sudo().write({
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
        parcelas_pagas = self._tem_parcelas_pagas()
        if len(parcelas_pagas) > 0:
            raise ValidationError('Contrato com %s parcelas pagas. Não pode ser cancelado!' %  (len(parcelas_pagas)))
        else:
            self._set_state_parcelas('cancelado')
    
    def _suspende_parcelas_financeiro(self):
        _logger.info("SUSPENDENDO PARCELAS FINANCEIRO")
        parcelas_nao_pagas = self.env['geracad.curso.financeiro.parcelas'].search([
            ('contrato_id','=',self.id),('state','=', 'vigente'),('esta_pago','=', False)])
        for parcela in parcelas_nao_pagas:
            parcela.write({
                'state': 'supenso'
            })

    def _reativa_parcelas_financeiro(self, valor_da_parcela, data_vencimento_parcelas):
        """ 
            Utilizado quando contrato suspenso e reativa, modificando os valores e as datas de vencimento das parcelas
            do contrato
        """
        _logger.info("REATIVANDO PARCELAS FINANCEIRO")
        self.search([('', '=', ), ...], offset=0, limit=None, order=None, count=False)
        parcelas_suspensas = self.env['geracad.curso.financeiro.parcelas'].search([
            ('contrato_id','=',self.id),('state','=', 'suspenso'),('esta_pago','=', False)], order='name ASC')
        number=0
        for parcela in parcelas_suspensas:
            parcela.write({
                'state': 'vigente',
                'valor': valor_da_parcela,
                'date_vencimento': data_vencimento_parcelas + relativedelta(months=(number)),
            })
             
        
    def _tem_parcelas_pagas(self):

        _logger.debug("PROCURANDO PARCELAS PAGAS")
        parcelas_pagas = self.env['geracad.curso.financeiro.parcelas'].search([
           '&', 
           ('contrato_id','=',self.id),
           '&',
           ('esta_pago','=', True),
           '|',
           ('state','=', 'vigente'),
           ('state','=', 'draft')
           ],)
           
        _logger.debug(parcelas_pagas)
        return parcelas_pagas

    def _verifica_parcelas_abertas_financeiro(self):
        
        _logger.info("VERFICANDO PARCELAS EM ABERTO")
        parcelas_abertas = self.env['geracad.curso.financeiro.parcelas'].search([
            ('contrato_id','=',self.id),('state','=', 'vigente'),('esta_pago','=', False)])
        parcelas_em_aberto = []
        for parcela in parcelas_abertas:
            diferenca = parcela.data_vencimento - date.today()

            if diferenca.days > 0:
                parcelas_em_aberto.append({
                    'data_vencimento': parcela.data_vencimento,
                    'dias_de_atraso': diferenca.days
                    
                })
        _logger.debug(parcelas_em_aberto)
        return parcelas_em_aberto
    
    def _number_to_text(self, value):
        return num2words(value, lang='pt_BR',to='currency').title()
    
    def get_date_str(self,date2str):
        '''
        Função retorna a data no formato ex. 'São Luís-MA, 20 de Abril de 2022'
        '''
        _logger.info(f"Data de assinatura:{date2str}")
        if not date2str:
            date2str = date.today()
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(date2str,format="long",locale=locale)
        return   date_str
    
    #TODO 
    # PROCURAR PARCELAS NA MATRICULA DO ALUNO E MUDAR O ESTADO TAMBÉM
    # POIS EXISTEM PARCELAS IMPORTADAS DO SISTEMA ANTIGO QUE NÃO TEM CONTRATO
    def _set_state_parcelas(self, state):
        for record in self:
            _logger.debug("Verificando Parcelas do Contrato")
            _logger.debug(record)
            for parcela in record.parcelas_contrato_ids:
                parcela.sudo().write({
                    'state': state
                })

    """

            BUTTON ACTIONS

    """

    def action_confirma_contrato(self):
      
        if not self.parcelas_geradas:
            raise ValidationError('Contrato sem parcelas geradas. Gere as parcelas e confirme o contrato! ' )

        self.curso_matricula_id.write({
            'contrato_gerado' : 1,
        })
        self.write({
            'state': 'vigente',
            
           })
        
        self._set_state_parcelas('vigente')

 

    def action_gera_parcelas(self):
        _logger.debug("GERANDO PARCELAS")
        if self.parcelas_geradas:
            raise ValidationError('Contrato com parcelas já geradas. ' )

        self._gera_parcelas_financeiro(self.qtd_parcelas,self.valor_parcelas)
        self.write({
            'parcelas_geradas': True
           })
        
        
        
    def action_cancela_contrato(self):
        self._cancela_parcelas_financeiro()
        self.curso_matricula_id.write({
            'contrato_gerado' : False,
            
        })
        self.write({
            'parcelas_geradas' : False,
            'state': 'draft',
        })
       
    
    def action_suspender_contrato(self):
        self._sspende_parcelas_financeiro()
        self.curso_matricula_id.write({
            'contrato_gerado' : True
        })
        self.write({
            'state': 'draft',
           })

    def action_reativar_contrato(self):
        self._reativa_parcelas_financeiro()
        self.curso_matricula_id.write({
            'contrato_gerado' : True
        })
        self.write({
            'state': 'draft',
           })

    def action_finaliza_contrato(self):
        parcelas_em_aberto = self._verifica_parcelas_abertas_financeiro()
        _logger.debug("parcelas em aberto")
        _logger.debug(parcelas_em_aberto)
        if len(parcelas_em_aberto) == 0:
            self.write({
                'state': 'finalizado',
            })
        else:
            raise ValidationError('Contrato com %s parcelas em aberto. Não pode ser finalizado!' % (len(parcelas_em_aberto)))



        

    
       