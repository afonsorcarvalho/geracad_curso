# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

#TODO
# Fazer botão de finalizar notas
# fazer estatísticas de notas (com média por curso, melhor nota etc)

class GeracadCursoNotaDisciplinaHistoricoFinal(models.Model):
    _name = "geracad.curso.nota.disciplina.historico.final"
    _description = "Notas de Disciplinas de Cursos do Histórico Final"
    _check_company_auto = True
    _order = 'aluno_nome'
  
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
    disciplina_id = fields.Many2one(
        "geracad.curso.disciplina",
        related='turma_disciplina_id.disciplina_id',
        readonly=True, 
        string='Disciplina',      
        store=True    
        )
    disciplina_nome = fields.Char(
        "Disciplina",
         related='turma_disciplina_id.disciplina_id.name',
        )
   
    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string="Matricula Curso",
        related='disciplina_matricula_id.curso_matricula_id',
        readonly=True,
        store=True
        
        )
    curso_matricula_codigo = fields.Char("Código",
        related='curso_matricula_id.name', 
        store=True,
        readonly=True
         )
         
    aluno_nome = fields.Char(
        string="Nome do Aluno",
        related='disciplina_matricula_id.curso_matricula_id.aluno_id.name',
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

    faltas = fields.Integer(
        string='Faltas',
        default=0,
        tracking=True,
        group_operator="avg",
    )
    
    periodo = fields.Integer(
        string='Período'
       
    )
    carga_horaria = fields.Integer(
        string='Carga Horária'
       
    )
   
   

    
    nota_1 = fields.Float(group_operator="avg", tracking=True)
    nota_2 = fields.Float(group_operator="avg",tracking=True)
    final = fields.Float(group_operator="avg",tracking=True)
    media = fields.Float("Média" , 
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
    
    
   

    """

            BUTTON ACTIONS

    """
  

