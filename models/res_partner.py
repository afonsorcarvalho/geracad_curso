# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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