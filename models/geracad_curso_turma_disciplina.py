# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoTurmDisciplina(models.Model):
    _name = "geracad.curso.turma.disciplina"
    _description = "Turmas de disciplina de Curso"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )

    disciplina_id = fields.Many2one(
        'geracad.curso.disciplina',
        string='Disciplina',
        required=True, 
        # domain=lambda self: self._get_disiplina_id_domain()
        
        )
    
    def _get_disiplina_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        return res

    disciplina_nome = fields.Char("Disciplina", 
        related='disciplina_id.name',
        readonly=True,
        store=True
    )
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Curso',
        )
    
    # curso_turma_nome = fields.Char("Código Curso", 
    #     related='curso_turma_id.name',
    #     readonly=True,
    #     store=True
    # )
    curso_id = fields.Many2one(
        string = "Curso", 
        related='curso_turma_id.curso_id',
        readonly=True,
        store=True
    )
    
    
    periodo = fields.Integer(
        string = "Periodo", 
        compute = "_compute_dados_grade",
        readonly=True,
        store=True
        
    )

    carga_horaria = fields.Integer(
        string = "Periodo", 
        compute = "_compute_dados_grade",
        readonly=True,
        store=True
        
    )
   
   
    @api.depends('curso_turma_id','disciplina_id') 
    def _compute_dados_grade(self):
        for record in self:
            grade_id = self.env['geracad.curso.grade'].search([
                ('disciplina_id', '=', record.disciplina_id.id  ),
                ('curso_id', '=', record.curso_id.id  )], 
                offset=0, limit=1, order=None, count=False)
            
            record.periodo = grade_id.periodo
            record.carga_horaria = grade_id.disciplina_id_carga_horaria
        
  
   
    matricula_aberta = fields.Boolean(string="Matrícula Aberta", default=True)
    
    data_abertura = fields.Date(
        string='Data Abertura',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    data_inicio = fields.Date(
        string='Inicio das aulas',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    data_previsao_termino = fields.Date(
        string='Previsão de término',
        default=fields.Date.context_today,
        track_visibility='true'
    )

    data_encerramento = fields.Date(
        string='Data Encerramento',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    professor_id =  fields.Many2one(
        'res.partner',
        string='Professor',
        required=True,
        domain=[('e_professor','=', True)]
        )
   
    vagas = fields.Integer(
        string='Vagas',track_visibility='true'
    )
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('aberta', 'Matrícula Aberta'),
        ('encerrada', 'Matrícula Encerrada'),
        ('suspensa', 'Matrícula Suspensa'), 
        ('em_andamento', 'Em andamento'), 
        ('cancelada', 'Cancelada'),
    ], string="Status", default="draft", track_visibility='true')

    sala_id = fields.Many2one(
        'geracad.curso.sala',
        string='Sala',
    )

    carga_horaria = fields.Char("Carga Horária")
    e_pendencia = fields.Boolean("É pendência")
    e_aproveitamento = fields.Boolean("É aproveitamento")

    alunos_count = fields.Integer(
        string='Alunos', 
        compute='_compute_alunos_count',
            
        )
    notas = fields.One2many('geracad.curso.nota.disciplina', 'turma_disciplina_id')
    active = fields.Boolean(default=True)
    


    def _compute_alunos_count(self):
        for record in self:    
            record.alunos_count = self.env["geracad.curso.matricula.disciplina"].search(
                [('turma_disciplina_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)

    
    
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
        vals['name'] = self._gera_codigo_turma(vals) or _('New')
        vals['state'] = 'aberta'
        
        result = super(GeracadCursoTurmDisciplina, self).create(vals)
        return result
    
    
    
    @api.depends('name', 'disciplina_id')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.name + '] ' + record.disciplina_id.name
            result.append((record.id, name))
        return result
    
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
    
    
    
    
    def _gera_codigo_turma(self,vals):
        """
            Gera o codigo da turma de cursos pegando o codigo da unidade, o codigo do curso, o ano que foi criada a turma, 
            qual o turno MAT=3, VES=2, NOT=1 e um número sequencial
        """
        date_now = date.today()
        _logger.info("Ano ")
        _logger.info(date_now.strftime("%y"))

        company = self.env['res.company'].search([('id', '=', vals['company_id'])])
        _logger.info(company.name)
        disciplina = self.env['geracad.curso.disciplina'].search([('id', '=', vals['disciplina_id'] )])
        _logger.info(disciplina.name)
        
        codigo_turma = ''
        codigo_turma += disciplina.codigo + "."
        codigo_turma += date_now.strftime("%y%m")+"."
        codigo_turma += self._get_number_sequencial(codigo_turma)
        _logger.info(codigo_turma)
        return codigo_turma

    

    def _get_number_sequencial(self, codigo_turma):

        _logger.info('PROCURANDO NOME DE TURMA:')
        _logger.info(codigo_turma)
        turmas = self.env['geracad.curso.turma.disciplina'].search([('name', '=like', codigo_turma+"%")], order="name asc")
        
        if len(turmas) == 0:
            _logger.info('NENHUMA TURMA ENCONTRADA')
            return "01"
        _logger.info('TURMAS ENCONTRADAS')
        for turma in turmas:
            _logger.info('TURMAS ENCONTRADAS')
            _logger.info(turma.name)
            _logger.info(turma.name[-2:])
            number_sequencial_string = turma.name[-2:]
            number_sequencial = int(number_sequencial_string)+1
        resultado_string ="{:02d}"
        return resultado_string.format(number_sequencial)
    
    """

            BUTTON ACTIONS

    """

    def action_go_alunos_disciplinas(self):
        _logger.info("action open alunos disciplinas")

        return {
            'name': _('Alunos'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
                'group_by': ['state'],
                'expand': True
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


    def action_suspender_matricula(self):
        self.write({
            'state': 'suspensa',
            'matricula_aberta': False,

        })

    def action_encerrar_matricula(self):
        self.write({
            'state': 'encerrada',
            'matricula_aberta': False,
            })
    
    def action_cancelar_matricula(self):
        self.write({
            'state': 'cancelada',
            'matricula_aberta': False,
            })

    def action_abrir_matricula(self):
        self.write({
            'state': 'aberta',
            'matricula_aberta': True,
            })

        

    
       