# -*- coding: utf-8 -*-

from ast import For

from odoo import models, fields, api, _
from datetime import date
from babel.dates import format_datetime, format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

import logging

_logger = logging.getLogger(__name__)



class GeracadCursoTurmDisciplina(models.Model):
    _name = "geracad.curso.turma.disciplina.aulas"
    _description = "Aulas da Turma de disciplina de Curso"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    
    

    name = fields.Char("Assunto")
    company_id = fields.Many2one(
        'res.company',string="Unidade", required=True, default=lambda self: self.env.company
    )
    
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        required=True, 

        )
    disciplina_id = fields.Many2one(
        string='Disciplina',
        related='turma_disciplina_id.disciplina_id',
        readonly=True,
        store=True
        )

    curso_id = fields.Many2one(
        string='Curso',
        related='turma_disciplina_id.curso_id',
        readonly=True,
        store=True
        )

    hora_inicio_agendado = fields.Datetime(
        string='Inicio Programado',
        default=fields.Datetime.now,
        tracking=True,
        required=True
    )
    hora_termino_agendado = fields.Datetime(
        string='Término Programado',     
        default= lambda self: date.today() +  relativedelta(hours=1),
        tracking=True,    
        required=True
    )

    hora_inicio = fields.Datetime(
        string='Inicio',
        tracking=True
    )

    hora_termino = fields.Datetime(
        string='Término',       
        tracking=True
    )
   
    tipo_de_aula = fields.Selection(string='Tipo', selection=[
        ('teorica', 'Teórica'),
        ('pratica', 'Prática'),
        ('teorica_pratica', 'Teórica e Prática'),
        ('avaliacao', 'Avaliação'),
        ], required=True)

    professor_id =  fields.Many2one(
        'res.partner',
        string='Professor',
        required=True,
        domain=[('e_professor','=', True)]
        )
 
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em andamento'),
        ('concluida', 'Concluída'),      
        ('cancelada', 'Cancelada'),
        
    ], string="Status", default="draft", tracking=True)

    sala_id = fields.Many2one(
        'geracad.curso.sala',
        string='Sala',
    )
    descricao = fields.Html("Descrição")
    
    active = fields.Boolean(default=True)
    

    #usado na impressão do diário
    def get_diario_date(self):
        '''
            Função que retorna uma string da data para impressão do diário
            no formato: ex. São Luis-MA, 02 de agosto de 2022
        '''
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(self.data_encerramento,format="long",locale=locale)
        return   date_str

    #usado na impressão da ata
    def get_ano_semestre(self,tipo):
        '''
            Função que retorna uma string  do ano ou do semestre da
            turma disciplina
        '''
        if tipo == "semestre":
            if(self.data_abertura.month > 6):
                return '2º'
            else:
                return '1º'
        if tipo == "ano":
            return self.data_abertura.year


    #apaga os filtros que não serão possível fazer procura
    def get_fields_to_ignore_in_search(self): 
        
        return [ 'message_needaction',
           
            'create_date',
            'create_uid',
            'message_channel_ids',
            'message_attachment_count',
            'message_follower_ids',
            'message_has_error',
            'message_has_error_counter',
            'message_has_sms_error',
            'message_ids',
            'message_is_follower',
            'message_main_attachment_id',
            'message_needaction',
            'message_needaction_counter',
            'message_partner_ids',
            'message_unread',
            'message_unread_counter',
            'website_message_ids',
            'write_date',
            'write_uid',
            '__last_update',
            
            ]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(GeracadCursoTurmDisciplina, self).fields_get(allfields, attributes=attributes)
        _logger.info(res)
        for field in self.get_fields_to_ignore_in_search():

            if res.get(field):
                res[field]['searchable'] = False 
                res[field]['selectable'] = False 
                res[field]['sortable'] = False     
                res[field]['exportable'] = False 
        return res

    # def _compute_alunos_count(self):
    #     for record in self:    
    #         record.alunos_count = self.env["geracad.curso.matricula.disciplina"].search(
    #             [('turma_disciplina_id', '=', record.id)],
    #             offset=0, limit=None, order=None, count=True)

        
    # @api.depends('name', 'disciplina_id')
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         name = '[' + record.name + '] ' + record.disciplina_id.name
    #         result.append((record.id, name))
    #     return result
    
    #TODO
    # Verificar essa função que não está funcionando direito

    # @api.model
    # def name_search(self, name, args=None, operator='=ilike', limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = [
    #             '|', ('name', '=ilike', name), ('disciplina_id', operator, name)
    #         ]
            
    #     records = self.search(domain + args, limit=limit)
    #     return records.name_get()
    
    
    
    
    
    """

            BUTTON ACTIONS

    """

    def action_go_alunos_disciplinas(self):
        _logger.info("action open alunos disciplinas")

        return {
            'name': _('Alunos Matriculados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
               
            }
        }
    def action_go_notas_disciplinas(self):
        _logger.info("action open alunos disciplinas")

        return {
            'name': _('Notas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.nota.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
                
                'expand': True,
                'editable': "bottom",
            }
        }


   
   
    def action_agendar(self):
        _logger.inf("finalizando")

    def action_iniciar(self):
        _logger.inf("finalizando")

    def action_finalizar(self):
        _logger.inf("finalizando")



        

    
       