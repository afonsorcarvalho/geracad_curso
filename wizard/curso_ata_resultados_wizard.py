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
    """
    This wizard is used to generate the final course results report.
    """
    _name = "geracad.curso.ata.resultados.wizard"
    _description = "Assistente de imprimir ata de resultados finais de curso"

    
    curso_turma_id = fields.Many2one('geracad.curso.turma',                             
        required=True        
    )

    tipo = fields.Selection([('situation', 'Situação'),('media', 'Média')], default='situation')
    apenas_formados = fields.Boolean()
   
    def _monta_disciplina(self,dado):
        """
        Builds a dictionary containing discipline data for a student.

        Args:
            dado (geracad.curso.nota.disciplina): The course grade data.

        Returns:
            dict: A dictionary with discipline information.
        """
        return {dado.disciplina_id.name : {
            'situation': dado.situation,
            'media': dado.media,
            'periodo': dado.periodo,
            }}
    # def _get_state_matricula(self):
    #     matriculas = self.env["geracad.curso.matricula"].search([('curso_turma_id','=', self.curso_turma_id.id),('state','not in',['cancelada','trancado','abandono'])], order="nome_aluno")
    #     return matriculas.mapped(lambda x: {x.nome_aluno: {'state': x.state}})                                                                                                                                                                                                                                                               
        
    
    def get_disciplinas_grade(self):
        """
        Get a list of course disciplines.

        Returns:
            list: A list of course disciplines and their count in each period.
        """
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
        """
        Retrieve student grades and organize them by student and discipline.

        Returns:
            dict: A dictionary containing student grades.
        """
        _logger.info("GET DATA")
        notas = []
        notas = self.env["geracad.curso.nota.disciplina"].search([
            ('curso_turma_id','=', self.curso_turma_id.id),
          #  ('disciplina_matricula_state','not in',['cancelada','trancado','abandono']),
          # ('situation','not in',['CA','TR'])
            
            ],order="aluno_nome ASC, periodo ASC")
        if self.apenas_formados:
            notas = notas.filtered(lambda r: r.curso_matricula_id.state in ['formado'])
        
        #pegando as disciplinas
        
        lines = {}
        disciplinas = {}
        for nota in notas:
            aluno = nota.aluno_nome
            _logger.info(f"Nota: {nota.aluno_nome}")
            _logger.info(f"Aluno: {aluno}")
            _logger.info(f"Disciplinas: {disciplinas.get(aluno)}")
            if disciplinas.get(aluno) != None:

                disciplinas[aluno].update(self._monta_disciplina(nota))
                _logger.info(f"Disciplinas: {disciplinas}")
                lines.update({nota.aluno_nome : {'disciplinas': disciplinas[aluno],'situacao_matricula': nota.curso_matricula_id.state}})   
            else:
                lines.update({
                    nota.aluno_nome : {'disciplinas':self._monta_disciplina(nota), 'situacao_matricula': nota.curso_matricula_id.state}
                })
                disciplinas[aluno] = (self._monta_disciplina(nota))
        _logger.info(lines)
        return lines
            
    def get_date_str(self):
        """
        Format the current date into a localized string.
        formato ex. 'São Luís-MA, 20 de Abril de 2022'
        Returns:
            str: The formatted date string.
        """
        
        date_hoje = date.today()
        locale = get_lang(self.env).code

       
        date_str = self.env.user.company_id.city_id.name + '-' + self.env.user.company_id.state_id.code + ', ' + format_date(date_hoje,format="long",locale=locale)
        return   date_str

    def action_confirm(self):
        """
        Perform the confirmation action to generate the report.

        Returns:
            dict: A report action.
        """
        _logger.debug("confirmado")
        if not self.curso_turma_id:
            raise ValidationError('Nenhuma Turma foi selecionada')
        return self.env.ref("geracad_curso.action_ata_resultados_report").report_action(self)
       
