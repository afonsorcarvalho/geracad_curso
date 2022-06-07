# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta


class GeracadCurso(models.Model):

    _name = "geracad.curso"
    _description = "Gerenciamento de cursos"

    _inherit = ['mail.thread']
  
    

    name = fields.Char()
    sigla = fields.Char()
    resolucao = fields.Char("Resolução")
    type_curso = fields.Many2one(
        string="Tipo do Curso",
        comodel_name="geracad.curso.type",
        domain="[]",
        context={},
        ondelete="restrict",
        help="Tipo do curso",
        required=True
        
    )
    quantidade_de_periodos = fields.Integer(string="Quantidade de Períodos")
    grade_id = fields.One2many(
        string="Grade Curricular",
        comodel_name="geracad.curso.grade",
        inverse_name="curso_id",
        domain="[]",
        context={},
        help="Explain your field.",
    )
    carga_horaria_total = fields.Integer(string="Carga Horária", compute='_compute_carga_horaria_total')

    
    
    

    _sql_constraints = [
        ('sigla_uniq', 'unique (sigla)',
         'Esta Sigla já está em uso por outro Curso!')
    ]

    @api.onchange('sigla')
    def set_caps(self):
        if self.sigla:
            val = str(self.sigla)
            self.sigla = val.upper()

    @api.depends('grade_id')
    def _compute_carga_horaria_total(self):
        for record in self:
            sum = 0
            for grade_line in record.grade_id:
                sum += grade_line.disciplina_id_carga_horaria
        record.carga_horaria_total = sum

   
class GeracadCursoType(models.Model):
    _name = "geracad.curso.type"
    _description = "Tipo do Curso"

    name = fields.Char()

class GeracadCursoDisciplina(models.Model):
    _name = "geracad.curso.disciplina"
    _description = "Disciplinas dos cursos"
    _inherit = ['mail.thread']

    name = fields.Char()
    codigo = fields.Char("Código", default=lambda self: _('New'))

    metodologia = fields.Many2one(
        string='Metodologia',
        comodel_name='geracad.curso.disciplina.metodologia',
        ondelete='set null',
    )
    carga_horaria = fields.Integer(string='Carga Horária')
   
    ementa = fields.Html(
        string='Ementa',
    )
   
    @api.model
    def create(self, values):
        if values.get('codigo', _('New')) == _('New'):
            values['codigo'] = self.env['ir.sequence'].next_by_code('disciplina.sequence') or ('New')
            

        result = super(GeracadCursoDisciplina,self).create(values)
        
        return result
    _sql_constraints = [
        ('codigo_disciplina_uniq', 'unique (codigo)', 'Este codigo já está sendo usado por uma disciplina !'),
    ]
    
    
    
class GeracadCursoDisciplinaMetodologia(models.Model):
    _name = "geracad.curso.disciplina.metodologia"
    _description = "Metodologia da Disciplina"

    name = fields.Char()

class GeracadCursoGrade(models.Model):
    _name = "geracad.curso.grade"
    _description = "Grade Curricular do Curso"
    
    _order = "periodo,sequence asc"
    
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_field' )

    sequence = fields.Integer(string="Sequência")
    e_obrigatoria = fields.Boolean("É obrigatória")
    e_excluida = fields.Boolean("Excluída")

    active = fields.Boolean("Está Ativa")
    periodo = fields.Integer(string="Periodo")
    curso_id = fields.Many2one(comodel_name='geracad.curso', string="Curso") 
    disciplina_id = fields.Many2one(comodel_name='geracad.curso.disciplina', string="Disciplina")
    disciplina_id_carga_horaria = fields.Integer(string="Carga Horária", 
        related='disciplina_id.carga_horaria',
        readonly=True,
        )
    
    
    @api.depends('disciplina_id')
    def _compute_field(self):
        for record in self:
            record.name = record.disciplina_id.name
          

class GeracadSala(models.Model):
    _name = "geracad.curso.sala"
    _description = "Salas de aula"

    name = fields.Char("Nome da Sala")
    description = fields.Text("Descrição")
    unidade = fields.Many2one(comodel_name='geracad.curso.unidade',string='Unidade', ondelete='restrict')
   
class GeracadUnidade(models.Model):
    _name = "geracad.curso.unidade"
    _description = "Unidades"
    name = fields.Char("Nome da Unidade")
    siglas = fields.Char("Siglas")

    company_id = fields.Many2one(
        string='Company', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )