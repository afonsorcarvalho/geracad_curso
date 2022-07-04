# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoHistorioFinal(models.Model):
    _name = "geracad.curso.historico.final"
    _description = "Histórico Final de Cursos"
   
    name = fields.Char("Código Matricula")

    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    carga_horaria = fields.Integer(
        string='Carga Horaria',
    )

    matricula_disciplina_id =  fields.Many2one(
        'geracad.curso.matricula.disciplina',
        string='Matrícula Disciplina',
        )
    disciplina_id =  fields.Many2one(
        'geracad.curso.disciplina',
        string='Disciplina',
        related='matricula_disciplina_id.disciplina_id',
        readonly=True,
        store=True
        )
    disciplina_name = fields.Char("Disciplina Nome",
        related = 'matricula_disciplina_id.disciplina_id.mame'
        readonly=True,
        store=True
    )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string="Matricula Curso",
        related='matricula_disciplina_id.curso_matricula_id',
        readonly=True,
        store=True       
        )

    curso_matricula_state = fields.Selection( 
        string="State Curso",
        related='matricula_disciplina_id.state',
        readonly=True,
        store=True
    )
    
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string="Turma Curso",
        related='matricula_disciplina_id.curso_matricula_id.curso_turma_id',
        readonly=True,
        store=True
        )

    curso_id = fields.Many2one(
        'geracad.curso',
        related='matricula_disciplina_id.curso_matricula_id.curso_turma_id.curso_id',
        readonly=True,
        store=True
        )

    curso_registro = fields.Char(
        'Curso Registro',
        )

    data_inicio = fields.Date()

    data_fim = fields.Date()

    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        related='matricula_disciplina_id.turma_disciplina_id',
        readonly=True,
        store=True,
        )

    professor_id = fields.Many2one(
        "res.partner",
        string='Professor',
        related='matricula_disciplina_id.turma_disciplina_id.professor_id',
        readonly=True,
        store=True,
        )
    faltas = fields.Integer(
        string='Faltas',
        default=0,
        tracking=True,
        group_operator="avg",
    )
    
    periodo = fields.Integer(
        string='periodo',
    )

    nota_1 = fields.Float(group_operator="avg", tracking=True)
    nota_2 = fields.Float(group_operator="avg",tracking=True)
    final = fields.Float(group_operator="avg",tracking=True)
    media = fields.Float("Média",  
    tracking=True,group_operator="avg",
    )
    situation = fields.Selection([
        ('AM', 'AM'), # aprovado por media
        ('AP', 'AP'), # aprovado por final
        ('RC', 'RC'), # reprovado por conteudo
        ('RF', 'RF'), # repovado por Falta
        ('IN', 'IN'), # inscrito
        ('CA', 'CA'), # cancelado
        ('TR', 'TR'), # trancado
        ('AB', 'AB'), # abandono
        ('EA', 'EA'), # estudos aproveitados
        ('FA', 'FA'),
        ], default='IN', string="Situação",tracking=True)

    
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('concluida', 'Concluída'),
    ], string="Status", default="draft", tracking=True)
    
    active = fields.Boolean(default=True)
    
    
   
 

   