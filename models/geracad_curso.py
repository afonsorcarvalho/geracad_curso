# -*- coding: utf-8 -*-

from email.policy import default
from odoo import models, fields, api, _
from datetime import datetime, timedelta

import logging

_logger = logging.getLogger(__name__)

class GeracadCurso(models.Model):

    _name = "geracad.curso"
    _description = "Gerenciamento de cursos"

    _inherit = ['mail.thread']
  
    

    name = fields.Char( tracking=True,)
    sigla = fields.Char( tracking=True,)
    resolucao = fields.Char("Resolução", tracking=True,)
    
    company_id = fields.Many2one(
        string='Unidade', 
        comodel_name='res.company', 
        required=True, 
        default=lambda self: self.env.user.company_id
    )
    
    type_curso = fields.Many2one(
        string="Tipo do Curso",
        comodel_name="geracad.curso.type",
        domain="[]",
        context={},
        ondelete="restrict",
        help="Tipo do curso",
        required=True
        
    )
    quantidade_de_periodos = fields.Integer(string="Quantidade de Períodos", tracking=True,)
    grade_version_ids = fields.One2many('geracad.curso.grade.versao', 'curso_id')
    grade_id = fields.One2many(
        string="Grade Curricular",
        comodel_name="geracad.curso.grade",
        inverse_name="curso_id",
        domain="[]",
        context={},
        help="Explain your field.s",
        tracking=True,
    )
    carga_horaria_total = fields.Integer(string="Carga Horária", compute='_compute_carga_horaria_total', tracking=True,)

    #função usada somente para atualizar grade para modo versão
    def atualiza_grade_modo_versao(self):
        _logger.info('AJEITANDO GRADE')
        curso_ids = self.search([])
        _logger.info('CURSOS ACHADOS')
        _logger.info(curso_ids)
        for curso in curso_ids:
            if len(curso.grade_version_ids)==0:
                grade_item_ids_list = []
                for grade_item in curso.grade_id:
                    _logger.info( 'ITEMS QUE SERAO ADICIONADO NA GRADE')
                    _logger.info(grade_item)
                    grade_item_ids_list.append(grade_item.id)
        
                grade_version_new = self.env['geracad.curso.grade.versao'].create({
                    'curso_id': curso.id,
                    'grade_ids':[(6,0,grade_item_ids_list)]
                })
                _logger.info('CRIADA VERSÃO')
                _logger.info(grade_version_new.name)
        
        
        
               

    
    

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

class GeracadEquivalenciaDisciplinas(models.Model):
    _name = "geracad.curso.equivalencia.disciplina"
    _description = "Equivalencia de disciplinas"
    _inherit = ['mail.thread']

    name = fields.Char("Nome", tracking=True,)
    disciplinas_equivalentes = fields.One2many(
        string='Disciplinas',
        comodel_name='geracad.curso.equivalencia.disciplina.line',
        inverse_name='equivalencia_disciplina_id' )

class GeracadEquivalenciaDisciplinasLine(models.Model):
    _name = "geracad.curso.equivalencia.disciplina.line"
    _description = "Line de equivalencia de disciplinas"

    equivalencia_disciplina_id = fields.Many2one(
         "geracad.curso.equivalencia.disciplina",
        string='Equivalencia Disciplinas',
        )
    disciplinas_equivalentes = fields.Many2one(
        "geracad.curso.disciplina",
        string='Disciplina',
        )

    codigo = fields.Char(
        string='Código',
        
        related='disciplinas_equivalentes.codigo',
        readonly=True,
 
    )
    carga_horaria = fields.Integer(
        string='Carga Horária',
        
        related='disciplinas_equivalentes.carga_horaria',
        readonly=True,
 
    )
    metodologia = fields.Many2one(
        string='Metodologia',
        
        related='disciplinas_equivalentes.metodologia',
        readonly=True,
 
    )
    

class GeracadCursoDisciplina(models.Model):
    _name = "geracad.curso.disciplina"
    _description = "Disciplinas dos cursos"
    _inherit = ['mail.thread']

    name = fields.Char( tracking=True,)
    codigo = fields.Char("Código", default=lambda self: _('New'), tracking=True,)

    metodologia = fields.Many2one(
        string='Metodologia',
        comodel_name='geracad.curso.disciplina.metodologia',
        ondelete='set null',
    )
    carga_horaria = fields.Integer(string='Carga Horária', tracking=True,)
   
    ementa = fields.Html(
        string='Ementa', tracking=True,
    )
    
    @api.model
    @api.depends('name', 'codigo')
    def name_get(self):
        result = []
        for record in self:
            if record.codigo:
                name = '[' + record.codigo + '] ' + record.name
            else:
                name = record.name
            result.append((record.id, name))
        return result
    
  
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = [
                '|', ('codigo', '=ilike', name), ('name', operator, name)
            ]
            
        records = self.search(domain + args, limit=limit)
        return records.name_get()
    
    
    
    
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


class GeracadCursoGradeVersao(models.Model):
    _name = "geracad.curso.grade.versao"
    _description = "Versão Grade Curricular do Curso"
    
    
    
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_field', tracking=True, )

    data_inicio = fields.Date("Data Início", default=fields.Date.context_today, tracking=True,
    )
    curso_id = fields.Many2one('geracad.curso', string="Curso",
    required=True
    ) 
    sequence = fields.Integer(string="Sequência")
    e_obsoleta =  fields.Boolean(string="Obsoleta", default=False)
    grade_ids = fields.One2many(
        string="Grade Curricular",
        comodel_name="geracad.curso.grade",
        inverse_name="version_grade_id",
        domain="[]",
        context={},
        help="Explain your field.s",
        tracking=True,
    )

    carga_horaria_total = fields.Integer(string="Carga Horária", compute='_compute_carga_horaria_total')

    @api.depends('curso_id')
    def _compute_field(self):
        for record in self:
            record.name = record.curso_id.sigla + '/' + str(record.data_inicio.year)
    
    @api.onchange('data_inicio')
    def _onchange_data_inicio(self):
        for record in self:
            record.name = record.curso_id.sigla + '/' + str(record.data_inicio.year)

    # @api.depends('curso_id')
    # def _default_name(self):
       
           
    #     return self.curso_id.sigla + '/' + str(self.data_inicio.year)

    @api.depends('grade_ids')
    def _compute_carga_horaria_total(self):
        for record in self:
            sum = 0
            for grade_line in record.grade_ids:
                sum += grade_line.disciplina_id_carga_horaria
        record.carga_horaria_total = sum

class GeracadCursoGrade(models.Model):
    _name = "geracad.curso.grade"
    _description = "Grade Curricular do Curso"
    
    _order = "periodo,sequence asc"
    
    _inherit = ['mail.thread']

    name = fields.Char(compute='_compute_field', tracking=True, )

    sequence = fields.Integer(string="Sequência")
    e_obrigatoria = fields.Boolean("É obrigatória", default=True)
    e_excluida = fields.Boolean("Excluída")

    version_grade_id = fields.Many2one(
        string='Versão',
        comodel_name='geracad.curso.grade.versao',
       
    )

    active = fields.Boolean("Está Ativa", default=True),
    periodo = fields.Integer(string="Periodo", tracking=True,)
    modulo = fields.Integer(string="Módulo", default=1, tracking=True,)
    curso_id = fields.Many2one(comodel_name='geracad.curso', string="Curso", 
    required=True
    ) 
    disciplina_id = fields.Many2one(comodel_name='geracad.curso.disciplina', string="Disciplina")
    disciplina_id_carga_horaria = fields.Integer(string="Carga Horária", 
        related='disciplina_id.carga_horaria',
        readonly=True,
        store=True,
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