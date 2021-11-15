# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoTurma(models.Model):
    _name = "geracad.curso.turma"
    _description = "Turmas de Cursos"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Código")
    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, default=lambda self: self.env.company
    )

    curso_id = fields.Many2one(
        'geracad.curso',
        string='Curso',
        )
   
    turno = fields.Selection(
        string='turno',
        selection=[('MAT', 'Matutino'), ('VES', 'Vespertino'),('NOT', 'Noturno')]
    )
    matricula_aberta = fields.Boolean(string="Matrícula Aberta", default=True)
    
    data_abertura = fields.Date(
        string='Data Abertura',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )

    data_encerramento = fields.Date(
        string='Data Encerramento',
        default=fields.Date.context_today,
        track_visibility='onchange'
    )
   
    vagas = fields.Integer(
        string='Vagas',track_visibility='onchange'
    )
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('aberta', 'Matrícula Aberta'),
        ('encerrada', 'Matrícula Encerrada'),
        ('suspensa', 'Matrícula Suspensa'), 
        ('cancelada', 'Cancelada'),
    ], string="Status", default="draft", track_visibility='onchange')

    unidade_id = fields.Many2one('geracad.curso.unidade', string="Unidade")

    matriculas_count = fields.Integer("Qtd Matriculas", compute="_compute_matriculas_count")

    active = fields.Boolean(default = True)

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
        vals['name'] = self._gera_codigo_turma(vals) or _('New')
        vals['state'] = 'aberta'
        
        result = super(GeracadCursoTurma, self).create(vals)
        return result
    
    
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
        curso = self.env['geracad.curso'].search([('id', '=', vals['curso_id'] )])
        _logger.info(curso.name)
        _logger.info(vals['turno'])
        codigo_turma = ''
        if(company.sigla):
            codigo_turma += company.sigla
        codigo_turma += curso.sigla
        codigo_turma += date_now.strftime("%y")
        codigo_turma += self._get_number_turno(vals['turno'])
        codigo_turma += self._get_number_sequencial(codigo_turma)
        _logger.info(codigo_turma)
        return codigo_turma

    def _get_number_turno(self, turno):
        _logger.info(turno)
        if turno == 'MAT':
            return '3'
        if turno == 'VES':
            return '2'
        if turno == 'NOT':
            return '1'
        return "ERROR"

    def _get_number_sequencial(self, codigo_turma):

        _logger.info('PROCURANDO NOME DE TURMA:')
        _logger.info(codigo_turma)
        turmas = self.env['geracad.curso.turma'].search([('name', '=like', codigo_turma+"%")], order="name asc")
        
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

    def _compute_matriculas_count(self):       
        for record in self:    
            record.matriculas_count = self.env["geracad.curso.matricula"].search(
                [('curso_turma_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
    
    """

            BUTTON ACTIONS

    """

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
    
    def action_go_matriculas(self):

        _logger.info("action open matriculas")
        
        return {
            'name': _('Matriculados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula',
            'domain': [('curso_turma_id', '=', self.id)],
        }
        


        

    
       