# -*- coding: utf-8 -*-

from ast import For
from email.policy import default

from odoo import models, fields, api, _
from datetime import date
from babel.dates import format_datetime, format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

import logging

_logger = logging.getLogger(__name__)



class GeracadCursoTurmaDisciplinaAulas(models.Model):
    _name = "geracad.curso.turma.disciplina.aulas"
    _description = "Aulas da Turma de disciplina de Curso"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    
    

    name = fields.Char("Assunto", 
    required=True
    )

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
        
    
    @api.depends('name', 'turma_disciplina_id')
    def name_get(self):
        result = []
        for record in self:
           
            name = '[' + str(record.turma_disciplina_id.disciplina_id.name) + '] ' + str(record.name)

           
            result.append((record.id, name))
        return result
    
        

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
    
        related='turma_disciplina_id.professor_id',
        readonly=True,
        store=True,
    
        )

    
    frequencia_ids = fields.One2many(
        string='Frequência',
        comodel_name='geracad.curso.turma.disciplina.aulas.frequencia',
        inverse_name='turma_aula_id',
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
        res = super(GeracadCursoTurmaDisciplinaAulas, self).fields_get(allfields, attributes=attributes)
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

    def _get_matriculas_ativas(self):
        _logger.info("Pegando matriculas ativas")
        matricula_disciplina_ids = []
        for rec in self:
            matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([
                '&',
                ('turma_disciplina_id','=',rec.turma_disciplina_id.id),
                ('state','in',['inscrito'])

                ])
        return matricula_disciplina_ids
            
            

    def _monta_frequencia(self):
        _logger.info("Montando a frequencia dos alunos")
        for rec in self:
            matricula_disciplina_ids = rec._get_matriculas_ativas()
            for matricula_disciplina in matricula_disciplina_ids:
                rec.write({
                    'frequencia_ids':[
                         (0,0, {
                        'turma_aula_id': rec.id,
                        'matricula_disciplina_id': matricula_disciplina.id,
                    })
                    ]
                   
                })


    def _calcula_adiciona_frequencia_na_nota_disciplina(self):
        _logger.info("Calculando e adicionando as faltas na turma")
        for rec in self:
            for frequencia in rec.frequencia_ids:
                soma = 0
                if frequencia.hora_1:
                    soma=soma+1
                if frequencia.hora_2:
                    soma=soma+1
                if frequencia.hora_3:
                    soma=soma+1
                if frequencia.hora_4:
                    soma=soma+1
                frequencia.matricula_disciplina_id.nota.faltas = frequencia.matricula_disciplina_id.nota.faltas + soma
   
    def action_agendar(self):
        _logger.info("agendando")
        for rec in self:
            rec.write({
                'state': 'agendada',
            })

    def action_iniciar(self):
        _logger.info("iniciando")
        for rec in self:
            rec._monta_frequencia()
            rec.write({
                'state': 'em_andamento',
                'hora_inicio': fields.Datetime.now()
            }
               
            )



    def action_finalizar(self):
        _logger.info("finalizando")
        _logger.info("iniciando")
        for rec in self:
            rec._calcula_adiciona_frequencia_na_nota_disciplina()
            rec.write({
                'state': 'concluida',
                'hora_termino': fields.Datetime.now()
            })

class GeracadCursoTurmaDisciplinaAulasFrequencia(models.Model):
    _name = "geracad.curso.turma.disciplina.aulas.frequencia"
    _description = "Frequencia das Aulas da Turma de disciplina de Curso"
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',string="Unidade", required=True, default=lambda self: self.env.company
    )

    turma_aula_id = fields.Many2one(
        'geracad.curso.turma.disciplina.aulas',
        string='Aulas',
        )
    matricula_disciplina_id = fields.Many2one(
        "geracad.curso.matricula.disciplina",
        string="Matrícula Disciplina"
    )
    curso_matricula_name = fields.Char(
      
        string='Matrícula',
        related='matricula_disciplina_id.curso_matricula_id.name',
        readonly=True,
        store=True
        )
    aluno_name = fields.Char(
     
        string='Aluno',
        related='matricula_disciplina_id.aluno_id.name',
        readonly=True,
        store=True
        )
    
    
    hora_1 = fields.Boolean("1ª hora", default=False)
    hora_2 = fields.Boolean("2ª hora", default=False)
    hora_3 = fields.Boolean("3ª hora", default=False)
    hora_4 = fields.Boolean("4ª hora", default=False)


        

    
       