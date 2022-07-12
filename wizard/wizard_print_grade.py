# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from tkinter.tix import Tree
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoWizardPrintGrade(models.TransientModel):
    _name = "geracad.curso.wizard.print.grade"
    _description = "Assistente para imprimir grade curricular do curso"

  
    curso_id = fields.Many2one(
        "geracad.curso", readonly=True, string="Curso"
    )
    grade_versao = fields.Many2one(
        "geracad.curso.grade.versao"
    )

    def print_grade(self):
        self.env.ref('geracad_curso.action_recibo_parcela_report')\
            .with_context({
                'curso_id': self.curso_id.id,
                'grade_versao': self.grade_versao.id 
                }).report_action(self)

    


    def action_confirm(self):
        """
           botao confirmação 
        """
        _logger.debug("confirmado impressão de grade curricular do curso")
        self.print_grade()
       
