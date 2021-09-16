# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatricula(models.Model):
    _name = "geracad.curso.matricula"
    _description = "matricula de Cursos"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código")
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Turma',
        required=True
        )
    curso_nome = fields.Char( 
        related='curso_turma_id.curso_id.name',
        string="Nome do curso",
        readonly=True,
        store=True
    )
    curso_turma_codigo = fields.Char( 
        related='curso_turma_id.name',
        string="Código da turma",
        readonly=True,
        store=True
    )
    aluno_id = fields.Many2one(
        'res.partner',
        string='Aluno',
        required=True,
        
        domain=[('e_aluno','=',True)]
        
        )   
   
    data_matricula = fields.Date(
        string='Data Matrícula',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )

    data_conclusao = fields.Date(
        string='Data Conclusão',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )
   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('inscrito', 'Inscrito'),
        ('trancado', 'Trancada'),
        ('abandono', 'Abandono'), 
        ('cancelada', 'Cancelada'),
        ('expulso', 'Expulso'), 
        ('falecido', 'Falecido'),
        ('formado', 'Formado'),
        
    ], string="Status", default="draft", track_visibility='onchange')


    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_turma_id_aluno_id_unique','UNIQUE(curso_turma_id, aluno_id)','Aluno já matriculado nessa turma') ]

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            curso_turma = self.env['geracad.curso.turma'].search([('id', '=', vals['curso_turma_id'] )])
            self = self.with_company(curso_turma.company_id)

        if vals.get('name', _('New')) == _('New'):
            seq_date = None
        vals['name'] = self._gera_codigo_matricula(vals) or _('New')
        vals['state'] = 'inscrito'
        
        result = super(GeracadCursoMatricula, self).create(vals)
        return result
    
    
    def _gera_codigo_matricula(self,vals):
        """
            Gera o codigo da matricula de cursos pegando o codigo da turma de curso + número sequencial
        """

        curso_turma = self.env['geracad.curso.turma'].search([('id', '=', vals['curso_turma_id'] )])
        _logger.info(curso_turma.name)
        
        
        codigo_matricula = curso_turma.name + "-"
        codigo_matricula += self._get_number_sequencial(curso_turma.name)
        _logger.info(codigo_matricula)
        return codigo_matricula

 

    def _get_number_sequencial(self, codigo_turma):

        _logger.info('PROCURANDO MATRICULAS NA TURMA:')
        _logger.info(codigo_turma)
        matriculas = self.env['geracad.curso.matricula'].search([('name', '=like', codigo_turma+"%")], order="name asc")
        
        if len(matriculas) == 0:
            _logger.info('NENHUMA MATRICULA ENCONTRADA')
            return "01"
        _logger.info('MATRICULAS ENCONTRADAS')
        for matricula in matriculas:
            
            _logger.info(matricula.name)
            _logger.info(matricula.name[-2:])
            number_sequencial_string = matricula.name[-2:]
            number_sequencial = int(number_sequencial_string)+1
        resultado_string ="{:02d}"
        return resultado_string.format(number_sequencial)
    
    """

            BUTTON ACTIONS

    """

    

        

    
       