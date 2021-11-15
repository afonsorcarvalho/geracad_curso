# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatriculaDisciplina(models.Model):
    _name = "geracad.curso.matricula.disciplina"
    _description = "matricula de Disciplinas de Cursos"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Nome")
    
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string='Matricula',
        required=True
        )
    curso_nome = fields.Char( 
        related='curso_matricula_id.curso_turma_id.curso_id.name',
        string="Nome do curso",
        readonly=True,
        store=True
    )
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        required=True
        
        )

    aluno_id = fields.Many2one(
        
        related = 'curso_matricula_id.aluno_id',
        string='Nome do Aluno',
        readonly=True,
        store=True,
        )   
    # aluno_nome = _id = fields.Many2one(
        
    #     related = 'curso_matricula_id.aluno_id.name',
    #     string='Nome do Aluno',
    #     readonly=True,
    #     store=True,
    #     )   
   
    data_matricula = fields.Date(
        string='Data Matrícula',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )

   
   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('inscrito', 'Inscrito'),
        ('cancelada', 'Cancelada'),
       
        
    ], string="Status", default="draft", track_visibility='onchange')


    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_matricula_id_turma_disciplina_id_unique','UNIQUE(curso_matricula_id, turma_disciplina_id)','Aluno já matriculado nessa disciplina') ]

    @api.model
    def create(self, vals):
        
        curso_matricula = self.env['geracad.curso.matricula'].search([('id', '=', vals['curso_matricula_id'] )])
        self = self.with_company(curso_matricula.company_id)

        vals['name'] = curso_matricula.name + " - " + curso_matricula.aluno_id.name
        vals['state'] = 'inscrito'
        
        result = super(GeracadCursoMatriculaDisciplina, self).create(vals)

        _logger.info("Criado Matricula")
        _logger.info(result)

        # criando as notas do aluno
        notas_disciplina = self.env['geracad.curso.nota.disciplina'].create(
            {
                "company_id": result.company_id.id,
                "disciplina_matricula_id": result.id,
                "turma_disciplina_id": result.turma_disciplina_id.id

            }
            )



        return result
    
    
  
    
    """

            BUTTON ACTIONS

    """

    

        

    
       