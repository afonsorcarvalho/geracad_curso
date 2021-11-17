# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

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
        string='Matricula',
        required=True
        )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        
        related='disciplina_matricula_id.curso_matricula_id',
        readonly=True,
        store=True
        
        )

    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        required=True
        
        )
    faltas = fields.Integer(
        string='Faltas',
        default=0
    )
    
    nota_1 = fields.Float()
    nota_2 = fields.Float()
    final = fields.Float()
    media = fields.Float("Média", compute="_compute_media")
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
        ], default='IN')


   
    # aluno_nome = _id = fields.Many2one(
        
    #     related = 'curso_matricula_id.aluno_id.name',
    #     string='Nome do Aluno',
    #     readonly=True,
    #     store=True,
    #     )   
   
   

   
   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('atualizada', 'Atualizada'),
        ('concluida', 'Concluida'),
       
        
    ], string="Status", default="draft", track_visibility='onchange')


    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_disciplina_matricula_id_turma_disciplina_id_unique','UNIQUE(disciplina_matricula_id, turma_disciplina_id)','Aluno já com notas nessa turma disciplina') ]

    
    
    
    @api.depends('nota_1', 'nota_2','final','faltas')
    def _compute_media(self):
        for record in self:
            record.media = (record.nota_1 + record.nota_2)/2
    
    
    
    
  
    
    """

            BUTTON ACTIONS

    """

    

        

    
       