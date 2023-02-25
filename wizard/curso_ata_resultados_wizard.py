# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class GeracadAtaResultadoCursoWizard(models.TransientModel):
    _name = "geracad.curso.ata.resultados.wizard"
    _description = "Assistente de imprimir ata de resultados finais de curso"

    
    curso_turma_id = fields.Many2one('geracad.curso.turma',                             
        required=True        
    )
   
    def _monta_disciplina(self,dado):
        return {dado.disciplina_id.name : {
            'situation': dado.situation,
            'media': dado.media,
            'periodo': dado.periodo,
            }}
    
    def get_disciplinas_grade(self):
        turma_curso_id = self.env["geracad.curso.turma"].search([('id','=', self.curso_turma_id.id)])
        grade_version = turma_curso_id.curso_grade_version
        grade_ids = grade_version.grade_ids
        disciplinas = []
        list_count_disciplinas_periodo = []
        periodo_index = 0
        sum_periodo = 0
        for lines in grade_ids:
            if lines.periodo:
                if periodo_index != lines.periodo:
                    periodo_index = lines.periodo
                    sum_periodo = 1
                    list_count_disciplinas_periodo.append(sum_periodo)
                else:
                    sum_periodo += 1
                    list_count_disciplinas_periodo[periodo_index-1] = sum_periodo
                
                disciplinas.append(lines.disciplina_id.name)
        #colocando estagio no final    
        #estagio = disciplinas.pop(0)
        #disciplinas.append(estagio)
        disciplinas.append(list_count_disciplinas_periodo)
        _logger.info(list_count_disciplinas_periodo)
        _logger.info(disciplinas)
        return disciplinas

    
    def get_dados(self):
        _logger.info("GET DATA")
        notas = []
        notas = self.env["geracad.curso.nota.disciplina"].search([('curso_turma_id','=', self.curso_turma_id.id)],order="aluno_nome ASC, periodo ASC")
       
        lines = {}
        for nota in notas:
            disciplinas = lines.get(nota.aluno_nome)
            _logger.info(disciplinas)
           
            if disciplinas:
               
                disciplinas.update(self._monta_disciplina(nota))
                lines.update({nota.aluno_nome : disciplinas})   
            else:
                lines.update({
                    nota.aluno_nome : self._monta_disciplina(nota)
                })
        _logger.info(lines)
        return lines
            
    def get_date_str(self):
        '''
        Função retorna a data no formato ex. 'São Luís-MA, 20 de Abril de 2022'
        '''
        date_hoje = date.today()
        locale = get_lang(self.env).code

       
        date_str = self.env.user.company_id.city_id.name + '-' + self.env.user.company_id.state_id.code + ', ' + format_date(date_hoje,format="long",locale=locale)
        return   date_str

    def action_confirm(self):
        """
            Action de confirmação de wizard para gerar relatório
        """
        _logger.debug("confirmado")
        if not self.curso_turma_id:
            raise ValidationError('Nenhuma Turma foi selecionada')
        return self.env.ref("geracad_curso.action_ata_resultados_report").report_action(self)
       
