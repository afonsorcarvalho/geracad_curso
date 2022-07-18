# -*- coding: utf-8 -*-

from setuptools import Require
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

#TODO
# Fazer botão de finalizar notas
# fazer estatísticas de notas (com média por curso, melhor nota etc)

class GeracadCursoNotaDisciplinaAproveitamento(models.Model):
    _name = "geracad.curso.nota.disciplina.aproveitamento"
    _description = "Aproveitamento de Notas de Disciplinas"
    _check_company_auto = True
    _order = 'aluno_nome'
  
    _inherit = ['mail.thread']
  
    name = fields.Char("Nome")
    
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string="Matricula Curso",    
        required=True   

        )
    curso_matricula_codigo = fields.Char("Código",
        related='curso_matricula_id.name', 
        store=True,
        readonly=True
         )
    aluno_nome = fields.Char(
       
        string="Nome do Aluno",
        related='curso_matricula_id.aluno_id.name',
        readonly=True,
        store=True
        
        )
    

    disciplina_matricula_id = fields.Many2one(
        'geracad.curso.matricula.disciplina',
        string='Matricula Disciplina',
       
        )
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        
        related='disciplina_matricula_id.turma_disciplina_id',
        readonly=True,
        store=True,
        )
    professor_id =  fields.Many2one(
        'res.partner',
        string='Professor',
        required=True,
        domain=[('e_professor','=', True)]
        )
    instituicao = fields.Char("Instituição", required=True)
    nome_disciplina_aproveitada = fields.Char("Disciplina Aproveitada", required=True)
    carga_horaria_aproveitada = fields.Integer(string='Carga Horária Aproveitada')
    data_aproveitamento = fields.Date(string='Data do Aproveitamento', default=fields.Date.context_today, )
    
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string="Turma Curso",
        related='curso_matricula_id.curso_turma_id',
        readonly=True,
        store=True
        
        )

    curso_id = fields.Many2one(
        'geracad.curso',
        related='curso_matricula_id.curso_turma_id.curso_id',
        readonly=True,
        store=True
        
        )

    turma_disciplina_data_abertura = fields.Date(
        string='Data de Abertura',
        related='disciplina_matricula_id.turma_disciplina_id.data_abertura',
        readonly=True,
        store=True,
        )

    disciplina_id = fields.Many2one(
        "geracad.curso.disciplina",
        string='Disciplina',      
        required="1"
        )

    faltas = fields.Integer(
        string='Faltas',
        default=0,
        tracking=True,
        group_operator="avg",
    )
     
    nota_1 = fields.Float(group_operator="avg", tracking=True)
    nota_2 = fields.Float(group_operator="avg",tracking=True)
    final = fields.Float(group_operator="avg",tracking=True)
    media = fields.Float("Média", 
        tracking=True,group_operator="avg",
    )
    
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('concluida', 'Concluída'),
    ], string="Status", default="draft", tracking=True)
    
    active = fields.Boolean(default=True)
    
       
    @api.constrains('faltas')
    def _check_faltas(self):  
        for record in self:
            if record.faltas < 0: 
                raise ValidationError("As faltas devem ser maio que 0 "  )
    
    @api.constrains('nota_1')
    def _check_nota_1(self):  
        for record in self:
            if record.nota_1 < 0 or record.nota_1 > 10.0:
                raise ValidationError("A nota 1 deve estar entre 0 e 10")
    
    @api.constrains('nota_2')
    def _check_nota_2(self):  
        for record in self:
            if record.nota_2 < 0 or record.nota_2 > 10.0:
                raise ValidationError("A nota 2 deve estar entre 0 e 10")
    
    @api.constrains('final')
    def _check_final(self):  
        for record in self:
            if record.final < 0 or record.final > 10.0:
                raise ValidationError("A nota Final deve estar entre 0 e 10")

    @api.depends('nota_1', 'nota_2','final')
    def _compute_media(self):
        for record in self:
            record.media = self._calcula_media(record.nota_1,record.nota_2,record.final)

    def _calcula_media(self,n1,n2,final):
        media = (n1 + n2)/2
        if(media < 7):
            if final > 0:
               media = (media + final)/2

        return media
        

    def _create_matricula_turma_disciplina(self):
        for rec in self:
            turma_disciplina_id = self.env["geracad.curso.turma.disciplina"].create({
                'curso_turma_id': rec.curso_matricula_id.curso_turma_id.id,
                'disciplina_id': rec.disciplina_id.id,
                'data_abertura': rec.data_aproveitamento,
                'data_inicio': rec.data_aproveitamento,
                'data_termino': rec.data_aproveitamento,
                'data_previsao_termino': rec.data_aproveitamento,
                'data_encerramento': rec.data_aproveitamento,
                'professor_id': rec.professor_id.id,
                'vagas': 1,
                
                
                'carga_horaria': rec.carga_horaria_aproveitada,
                'e_aproveitamento': True,               
            })

            if turma_disciplina_id:
                rec.write({ 'turma_disciplina_id' : turma_disciplina_id.id})
                matricula_disciplina_id = self.env["geracad.curso.matricula.disciplina"].create({
                    'curso_matricula_id': rec.curso_matricula_id.id,
                    'turma_disciplina_id': turma_disciplina_id.id,
                    'e_aproveitamento': True,
                })
                if matricula_disciplina_id:
                    nota = self.env["geracad.curso.nota.disciplina"].search([('disciplina_matricula_id','=',matricula_disciplina_id.id)])
                    nota.write({
                        'faltas': rec.faltas,
                        'nota_1': rec.nota_1,
                        'nota_2': rec.nota_2,
                        'media': rec.media,
                        'situation': 'EA',
                    })
            turma_disciplina_id.action_encerrar_turma_disciplina()
    """

            BUTTON ACTIONS

    """
    
    def action_lancar_nota(self):    
        _logger.debug("Nota Lançada")
        self._create_matricula_turma_disciplina()
        

        self.write({
            'state': 'concluida'
        })
        

