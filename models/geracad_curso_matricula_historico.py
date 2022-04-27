# -*- coding: utf-8 -*-
# NAO ESTÁ SENDO UTILIZADO ESSE  OBJETO
# APENAS CONSULTA COMO EXEMPLO
from odoo import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatriculaHistorico(models.AbstractModel):
    _name = 'report.geracad_curso_matricula.report_historico'
    _description = "Historico do aluno"

    aluno = "aluno de teste"
    
    def _disciplina_notas(self, periodo,matricula):
        _logger.debug("entrou em disciplina notas")
    

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #     register_ids = self.env.context.get('active_ids', [])
    #     model = self.env.context.get('active_model')
    #     docs = self.env[model].browse(self.env.context.get('active_ids', []))
    #     data['testando'] = "testando"
    #     for register_id in register_ids:
    #         matricula_id = self.env['geracad.curso.matricula'].search(
    #             [('id', '=', register_id )], offset=0, limit=None, order=None, count=False)
    #         _logger.debug("matricula id")
    #         _logger.debug(docids)
    #         _logger.debug(data)
    #     return {
    #         'aluno_id':{'name':'ai dentro'},
    #         'teste':"aqui é um teste de dado inserido",
    #         'disciplinas': self._disciplina_notas,
            
    #     }
            