# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatricula(models.Model):
    _name = "geracad.curso.matricula"
    _description = "matricula de Cursos"
    _check_company_auto = True


    
    _inherit = ['portal.mixin','mail.thread']
    


    name = fields.Char("Código")
    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, default=lambda self: self.env.company
        
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
    curso_id = fields.Many2one( 
        related='curso_turma_id.curso_id',
        string="Curso",
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
        track_visibility='true'
    )

    data_conclusao = fields.Date(
        string='Data Conclusão',
        default=fields.Date.context_today,
        track_visibility='true'
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
        
    ], string="Status", default="draft", readonly=False)

    matriculas_disciplina_ids = fields.One2many(
       
        comodel_name="geracad.curso.matricula.disciplina",
        inverse_name="curso_matricula_id",

    )

    matriculas_disciplinas_count = fields.Integer(
        string='Disciplinas', 
        compute='_compute_matriculas_disciplinas',
            
        )
    notas_disciplinas_count = fields.Integer(
        string='Disciplinas', 
        compute='_compute_notas_disciplinas',
            
        )
    contratos_count = fields.Integer(
        string='Contratos', 
        compute='_compute_contratos',
            
        )
    
    contrato_gerado = fields.Boolean("Gerado Contrato?", readonly=True)

    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_turma_id_aluno_id_unique','UNIQUE(curso_turma_id, aluno_id)','Aluno já matriculado nessa turma') ]
  
    def _compute_matriculas_disciplinas(self):
        for record in self:    
            record.matriculas_disciplinas_count = self.env["geracad.curso.matricula.disciplina"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
                
    def _compute_notas_disciplinas(self):
        for record in self:    
            record.notas_disciplinas_count = self.env["geracad.curso.nota.disciplina"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
   
    def _compute_contratos(self):
        for record in self:    
            record.contratos_count = self.env["geracad.curso.contrato"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)

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
    
    
    
    @api.depends('name', 'curso_turma_id')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.name + '] ' + record.aluno_id.name
            result.append((record.id, name))
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

    
    def _get_periodos(self):
        res = []
        for periodo in range(self.curso_id.quantidade_de_periodos):
                res.append(periodo+1)   
        return res  

    def _get_notas_periodo(self, periodo):
        
        nota_disciplina_ids = self.env['geracad.curso.nota.disciplina'].search([('curso_matricula_id', '=', self.id)])
        nota_disciplina_ids_periodo = []
        for nota_disciplina_id in nota_disciplina_ids:
            _logger.debug(nota_disciplina_id)
            if nota_disciplina_id.periodo == int(periodo):
                nota_disciplina_ids_periodo.append(nota_disciplina_id)
        
        return nota_disciplina_ids_periodo

    def _tem_notas_periodo(self,periodo):
        count_disciplinas = self.env['geracad.curso.nota.disciplina'].search([('curso_matricula_id', '=', self.id),('periodo', '=', periodo)], count=True)
        return count_disciplinas
    
    def _get_portal_return_action(self):
        """ Return the action used to display matriculas when returning from customer portal. """
        self.ensure_one()
        return self.env.ref('sale.action_quotations_with_onboarding')
    
    # url de acesso no portal
    def _compute_access_url(self):
        super(GeracadCursoMatricula, self)._compute_access_url()
        for matricula in self:
            matricula.access_url = '/my/matriculas/%s' % matricula.id
    # url de nome do aquivo download no portal
    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Histórico - %s' % (self.name)
    """

            BUTTON ACTIONS

    """
    def action_gerar_contrato(self):
        _logger.info("Gerando Contrato")
        return {
            'name': _('Gerar Contrato'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'form',
            'res_model': 'geracad.curso.contrato',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }

    def action_trancar(self):
        _logger.info("Matrícula Trancada")
        self.write({'state': 'trancado'})

    def action_go_matriculas_disciplinas(self):

        _logger.info("action open matriculas disciplinas")
        
        return {
            'name': _('Disciplinas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
                'group_by': ['state'],
                'expand': True
            }
        }
        
    def action_go_notas_disciplinas(self):

        _logger.info("action open notas disciplinas")
        
        return {
            'name': _('Notas Disciplinas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.nota.disciplina',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
     
            }
        }

    def action_go_contratos(self):

        _logger.info("action open notas disciplinas")
        
        return {
            'name': _('Gerar Contrato'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.contrato',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }
        

   

        

    
       