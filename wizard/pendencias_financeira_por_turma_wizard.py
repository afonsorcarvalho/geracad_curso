# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from tokenize import group
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class GeracadCursoPendenciasFinanceirasPorTurmaWizard(models.TransientModel):
    _name = "geracad.curso.pendencias.financeira.turma.wizard"
    _description = "Assistente de imprimir pendencias financeiras por turmas"

    
    
    
    turma_curso_ids =  fields.Many2one(
      
        "geracad.curso.turma" ,
        string='Cod. Turma',
        
    )
    
    
    data_vencimento_inicio = fields.Date("Data Vencimento Início")
    data_vencimento_fim = fields.Date("Data Vencimento Fim")
    data_pagamento_inicio = fields.Date("Data Pagamento Início")
    data_pagamento_fim = fields.Date("Data Pagamento Fim")

   
    
    
    def get_parcelas_por_turma(self, codigo_turma = ""):
        domain_filter = []
        resposta = []

        if self.data_vencimento_inicio and self.data_vencimento_fim:
           domain_filter.append(('data_vencimento','>=', self.data_vencimento_inicio))  
           domain_filter.append(('data_vencimento','<=', self.data_vencimento_fim))  
        if self.data_pagamento_inicio and self.data_pagamento_fim:
           domain_filter.append(('data_vencimento','>=', self.data_pagamento_inicio))  
           domain_filter.append(('data_vencimento','<=', self.data_pagamento_fim))  
       
        group_parcelas_ids = self.env['geracad.curso.financeiro.parcelas'].read_group(
            domain_filter, #domain
            ['curso_turma_codigo', 'valor:sum'], #fields
            ['curso_turma_codigo'] #group_by
        )
        
        for group_parcela in group_parcelas_ids:
            _logger.info(group_parcela["valor"])
            domain = domain_filter.copy()

            domain.append(('curso_turma_codigo','in',[group_parcela['curso_turma_codigo']]))
           
            #pegando valores pagos
            domain_pago = domain.copy()
            domain_pago.append(('esta_pago', '=', True ))
            group_parcelas_paga_ids = self.env['geracad.curso.financeiro.parcelas'].read_group(
                domain_pago, #domain
                ['curso_turma_codigo', 'valor:sum'], #fields
                ['curso_turma_codigo'] #group_by
            )
            if len(group_parcelas_paga_ids) == 0:
                parcelas_paga = {'valor': 0.0}
            else:
                for group_parcelas_paga in group_parcelas_paga_ids:
                    parcelas_paga = {'valor': group_parcelas_paga['valor']}
                    
            _logger.info(group_parcelas_paga_ids)
            #pegando valores abertos
            domain_aberto = domain.copy()
            domain_aberto.append(('esta_pago', '=', False ))
            group_parcelas_abertas_ids = self.env['geracad.curso.financeiro.parcelas'].read_group(
                domain_aberto, #domain
                ['curso_turma_codigo', 'valor:sum'], #fields
                ['curso_turma_codigo'] #group_by
            )
            if len(group_parcelas_abertas_ids) == 0:
                parcelas_aberta = {'valor': 0.0}
            else:
                for group_parcelas_abertas in group_parcelas_abertas_ids:
                    parcelas_aberta = {'valor': group_parcelas_abertas['valor']}

            #pegando valores vencidas
            domain_vencidas = domain.copy()
            domain_vencidas.append(('esta_pago', '=', False ))
            domain_vencidas.append(('data_vencimento','<', datetime.today()))
            group_parcelas_vencidas_ids = self.env['geracad.curso.financeiro.parcelas'].read_group(
                domain_vencidas, #domain
                ['curso_turma_codigo', 'valor:sum'], #fields
                ['curso_turma_codigo'] #group_by
            )
            if len(group_parcelas_vencidas_ids) == 0:
                parcelas_vencidas = {'valor': 0.0}
            else:
                for group_parcelas_vencidas in group_parcelas_vencidas_ids:
                    parcelas_vencidas = {'valor': group_parcelas_vencidas['valor']}

            #pegando valores a vencer
            domain_a_vencer = domain.copy()
            domain_a_vencer.append(('esta_pago', '=', False ))
            domain_a_vencer.append(('data_vencimento','>=', datetime.today()))
            group_parcelas_a_vencer_ids = self.env['geracad.curso.financeiro.parcelas'].read_group(
                domain_a_vencer, #domain
                ['curso_turma_codigo', 'valor:sum'], #fields
                ['curso_turma_codigo'] #group_by
            )
            if len(group_parcelas_a_vencer_ids) == 0:
                parcelas_a_vencer = {'valor': 0.0}
            else:
                for group_parcelas_a_vencer in group_parcelas_a_vencer_ids:
                    parcelas_a_vencer = {'valor': group_parcelas_a_vencer['valor']}

            resposta.append({
                    'curso_turma_codigo' : group_parcela['curso_turma_codigo'],
                    'valor_total' : group_parcela['valor'],
                    'valor_total_pago' : parcelas_paga['valor'],
                    'valor_total_abertas' : parcelas_aberta['valor'],
                    'valor_total_vencidas' : parcelas_vencidas['valor'],
                    'valor_total_a_vencer' : parcelas_a_vencer['valor'],
                    })
            _logger.info(resposta)

        return resposta

         



    def get_parcelas(self, status = 'todas', count = False, sum = False):

        
        
        domain_filter = []
        if status == 'todas':
            domain_filter = []
          
        if status == 'pagas':
            domain_filter.append(('esta_pago', '=', True ))
    
        if status == 'abertas':
            domain_filter.append(('esta_pago', '=', False ))
          
        if status == 'vencidas':
            domain_filter.append(('esta_pago', '=', False )) 
            domain_filter.append(('data_vencimento','<', datetime.today())) 
               
        if status == 'a_vencer':
            domain_filter.append(('esta_pago', '=', False )) 
            domain_filter.append(('data_vencimento','>=', datetime.today())) 
 
        if self.turma_curso_ids:
            turma_curso_codigos = []
            for turma_curso in self.turma_curso_ids:
                turma_curso_codigos.append( turma_curso.name)
            domain_filter.append(('curso_turma_codigo','in',turma_curso_codigos))
        if self.data_vencimento_inicio and self.data_vencimento_fim:
           domain_filter.append(('data_vencimento','>=', self.data_vencimento_inicio))  
           domain_filter.append(('data_vencimento','<=', self.data_vencimento_fim))  
        if self.data_pagamento_inicio and self.data_pagamento_fim:
           domain_filter.append(('data_vencimento','>=', self.data_pagamento_inicio))  
           domain_filter.append(('data_vencimento','<=', self.data_pagamento_fim))  
       
     
        parcelas = self.env['geracad.curso.financeiro.parcelas'].search(domain_filter, 
                offset=0, limit=100, order="data_vencimento ASC ", count=count
            )
        group_parcelas_ids = parcelas.read_group(
            domain_filter, #domain
            ['curso_turma_codigo', 'valor:sum'], #fields
            ['curso_turma_codigo'] #group_by
        )
        for group_parcela in group_parcelas_ids:
            _logger.info(group_parcela["valor"])
            
        _logger.info("parcela agrupada")
        _logger.info(group_parcelas_ids)
        soma = 0
        for parc in parcelas:
            soma +=parc.valor
        if sum: 
            return soma
        if not sum: 
            return parcelas
    
    def get_date_str(self):
        '''
        Função retorna a data no formato ex. 'São Luís-MA, 20 de Abril de 2022'
        '''
        date_hoje = date.today()
        locale = get_lang(self.env).code

       
        date_str = self.env.user.company_id.city_id.name + '-' + self.env.user.company_id.state_id.code + ', ' + format_date(date_hoje,format="long",locale=locale)
        return   date_str

    def action_confirm(self):
        """
        
        """
        _logger.debug("confirmado")
        return self.env.ref("geracad_curso.action_pendencias_financeira_turma_report").report_action(self)
       
