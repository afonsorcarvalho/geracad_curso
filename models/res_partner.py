# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)



class geracadCursoAluno(models.Model):
   
    
    _inherit = ['res.partner']

    matriculas_ids = fields.One2many(
       
        comodel_name="geracad.curso.matricula",
        inverse_name="aluno_id",

    )
    matriculas_disciplina_ids = fields.One2many(
       
        comodel_name="geracad.curso.matricula.disciplina",
        inverse_name="aluno_id",

    )
    turma_disciplina_ids = fields.One2many(
       
        comodel_name="geracad.curso.turma.disciplina",
        inverse_name="professor_id",

    )
    hora_aula = fields.Monetary(string='Valor Hora Aula')
    tipo_chave_pix = fields.Selection([
        ('cpf', 'CPF'),
        ('cnpj', 'CNPJ'),
        ('celular', 'Celular'),
        ('email', 'E-mail'),
        ('aleatorio', 'Aleatório')
        ], string = "Tipo de Chave")
        
    chave_pix = fields.Char(string='Chave Pix')
    banco = fields.Char(string='Banco')
    tipo_conta = fields.Selection([('conta_corrente','Conta Corrente'),('conta_poupanca','Conta Poupança')],string = "Tipo de Conta")
    agencia = fields.Char(string='Agência')
    conta = fields.Char(string='Conta')
    area_conheciemento = fields.Char("Área de conhecimento")
    formacao_academica = fields.Char("Formação Acadêmica")

    matriculas_curso_count = fields.Integer("Cursos Matriculados", compute="_compute_matriculas_curso_count")
    turmas_disciplinas_ministradas_count = fields.Integer("Disciplinas Ministradas", compute="_compute_turmas_disciplinas_ministradas_count")
    
    
    def _compute_matriculas_curso_count(self):
        self.matriculas_curso_count = len(self.matriculas_ids)
    
    def _compute_turmas_disciplinas_ministradas_count(self):
        self.turmas_disciplinas_ministradas_count = len(self.turma_disciplina_ids)
    
    def action_go_matriculas_disciplinas(self):
        _logger.info("action aluno open matriculas disciplinas")
        
        return {
            'name': _('Cursos Matriculados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula',
            'domain': [('aluno_id', '=', self.id)],
            'context': {
                'default_aluno_id': self.id,
                
            }
        }
        
    def action_go_turmas_disciplinas_ministradas(self):
        _logger.info("action professor open matriculas disciplinas")
        
        return {
            'name': _('Cursos Ministrados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.turma.disciplina',
            'domain': [('professor_id', '=', self.id)],
            'context': {
                'default_professor_id': self.id,
                
            }
        }
