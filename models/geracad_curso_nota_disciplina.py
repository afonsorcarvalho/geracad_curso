# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

#TODO
# Fazer botão de finalizar notas
# fazer estatísticas de notas (com média por curso, melhor nota etc)

class GeracadCursoNotaDisciplina(models.Model):
    _name = "geracad.curso.nota.disciplina"
    _description = "Notas de Disciplinas de Cursos"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Nome")
    
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    disciplina_matricula_id = fields.Many2one(
        'geracad.curso.matricula.disciplina',
        string='Matricula Disciplina',
        required=True
        )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string="Matricula Curso",
        
        related='disciplina_matricula_id.curso_matricula_id',
        readonly=True,
        store=True
        
        )
    curso_matricula_state = fields.Selection(
       
        string="State Curso",
        
        related='disciplina_matricula_id.state',
        readonly=True,
        store=True
    )
    
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string="Turma Curso",
        
        related='disciplina_matricula_id.curso_matricula_id.curso_turma_id',
        readonly=True,
        store=True
        
        )
    curso_id = fields.Many2one(
        'geracad.curso',
        
        related='disciplina_matricula_id.curso_matricula_id.curso_turma_id.curso_id',
        readonly=True,
        store=True
        
        )

    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        
        related='disciplina_matricula_id.turma_disciplina_id',
        readonly=True,
        store=True,
        
        
        
        )
    disciplina_id = fields.Many2one(
        "geracad.curso.disciplina",
        related='turma_disciplina_id.disciplina_id',
        
        readonly=True, 
        
        string='Disciplina',      
        store=True    
        )

    faltas = fields.Integer(
        string='Faltas',
        default=0
    )
    
    periodo = fields.Integer(
        string='periodo',
        compute="_compute_periodo",
        store=True
    )
    gerado_historico_final = fields.Boolean("Histórico final?")
   
    @api.depends('disciplina_matricula_id','curso_matricula_id')
    def _compute_periodo(self):
        for record in self:
            grade = self.env["geracad.curso.grade"].search([('curso_id','=',record.curso_id.id),('disciplina_id','=',record.disciplina_id.id)])
            record.periodo = grade.periodo

    
    nota_1 = fields.Float()
    nota_2 = fields.Float()
    final = fields.Float()
    media = fields.Float("Média", compute="_compute_media", 
    store=True
    )
    situation = fields.Selection([
        ('AM', 'AM'),
        ('AP', 'AP'),
        ('RC', 'RC'),
        ('RF', 'RF'),
        ('IN', 'IN'),
        ('CA', 'CA'),
        ('TR', 'TR'),
        ('AB', 'AB'),
        ('EA', 'EA'),
        ('FA', 'FA'),
        ], default='IN', string="Situação")


   
    # aluno_nome = _id = fields.Many2one(
        
    #     related = 'curso_matricula_id.aluno_id.name',
    #     string='Nome do Aluno',
    #     readonly=True,
    #     store=True,
    #     )   
   
   
    
   
   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('atualizando', 'Em atualização'),
        ('concluida', 'Concluída'),
       
        
    ], string="Status", default="draft", track_visibility='true')


    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_disciplina_matricula_id_turma_disciplina_id_unique','UNIQUE(disciplina_matricula_id, turma_disciplina_id)','Aluno já com notas nessa turma disciplina') ]

    
    
    
    @api.depends('nota_1', 'nota_2','final','faltas')
    def _compute_media(self):
        for record in self:
            record.media = (record.nota_1 + record.nota_2)/2
    
    
    
    
  
    
    

        

    
       