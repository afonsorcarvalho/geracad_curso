# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class GeracadMapaPagamentoCursoWizard(models.TransientModel):
    _name = "geracad.curso.mapa.pagamento.wizard"
    _description = "Assistente de imprimir mapa de pagamento por turma de curso"

    
    curso_turma_id = fields.Many2one('geracad.curso.turma',                             
        required=True        
    )
   
          
    def get_alunos(self):
        _logger.info("pegando alunos")
        matricula_ids = self.env[ "geracad.curso.matricula"].search([('curso_turma_id','=', self.curso_turma_id.id)],)
        return matricula_ids
    
    # def get_max_parcela(self):
    #     parcelas_ids = self.env["geracad.curso.financeiro.parcelas"].search([('curso_turma_codigo','=', self.curso_turma_id.name)], order="numero_parcela DESC")
    #     if parcelas_ids:
    #         return parcelas_ids[0].numero_parcela
    def get_parcelas_count_max(self):
        return list(range(1,self.get_max_parcela()+1))
    def get_max_parcela(self):
        parcela_max = self.curso_turma_id.curso_id.qtd_parcelas
        if parcela_max > 0:
            return parcela_max
        parcelas_ids = self.env["geracad.curso.financeiro.parcelas"].search([('curso_turma_codigo','=', self.curso_turma_id.name)], order="numero_parcela DESC")
        if parcelas_ids:
            return parcelas_ids[0].numero_parcela
        
    def get_parcelas_group(self):
        _logger.info("pegando parcelas dos alunos por mes")
        matricula_ids = self.env[ "geracad.curso.matricula"].search([('curso_turma_id','=', self.curso_turma_id.id)])
        
        parcelas_ids = self.env["geracad.curso.financeiro.parcelas"].read_group(domain=[
            ('curso_turma_codigo','=', self.curso_turma_id.name)
            ], groupby = ['numero_parcela'],fields=['numero_parcela','data_vencimento','valor'],lazy=False)
        # parcelas_ids.mapped(lambda r: {

        # }) 
        _logger.info(parcelas_ids)
        
        return parcelas_ids
    
    
    def get_dados(self):
        _logger.info("GET DATA")
        matricula_ids = self.get_alunos()
        matricula_ids = matricula_ids.sorted(key=lambda r: r.aluno_id.name)
        alunos_nome = matricula_ids.mapped('aluno_id.name')
        lines={}
        dict_parcelas={}
        parcelas_group = self.env["geracad.curso.financeiro.parcelas"].read_group(domain=[
            ('curso_turma_codigo','=', self.curso_turma_id.name)
            ], groupby = ['numero_parcela'],fields=['numero_parcela','data_vencimento','valor'],lazy=False)
        _logger.info(parcelas_group)
        # pegando parcelas por mês
        for matricula in matricula_ids: 
                domain = [('curso_matricula_id','=',matricula.id)]
                # montando o máximo de parcelas da turma
                parcela_ids =  self.env["geracad.curso.financeiro.parcelas"].search(domain,order="data_vencimento ASC")
                if not lines.get(matricula.aluno_id.name):
                    lines[matricula.aluno_id.name] = {'status_matricula': matricula.state,
                                                        'parcelas':{}
                                                      }
                for parcela_group in parcelas_group: 
                    #if not lines[matricula.aluno_id.name]['parcelas'].get(parcela_group.get('numero_parcela')):
                    lines[matricula.aluno_id.name]['parcelas'][parcela_group.get('id')] = {}  
                    
                for parcela in parcela_ids:
                    if parcela.state in ['vigente', 'draft']:
                        if parcela.data_vencimento < date.today():
                            state = 'vencido'
                        else:
                            state = 'aberta'
                    else:
                        state = parcela.state
                    lines[matricula.aluno_id.name] ['parcelas'][parcela.id] = {
                         'state': state,
                         'data_vencimento': parcela.data_vencimento
                        } 
                    
                    
                
                
        _logger.info(lines)               
         
                    
           
        return lines
            
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
            Action de confirmação de wizard para gerar relatório
        """
        _logger.debug("confirmado")
        if not self.curso_turma_id:
            raise ValidationError('Nenhuma Turma foi selecionada')
        return self.env.ref("geracad_curso.action_mapa_pagamento_turma_report").report_action(self)
       
