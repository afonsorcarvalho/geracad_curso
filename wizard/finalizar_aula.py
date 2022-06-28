# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoFinalizarAula(models.TransientModel):
    _name = "geracad.curso.finalizar.aula"
    _description = "Assistente de Finalizar aulas de Turmas de Disciplinas"

  
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina", readonly=True, string="Turma de Disciplina"
    )
    

    data_termino = fields.Date(
        string="Data do Término das Aulas",
        default=fields.Date.context_today,
        required=True,
    )
   

    def action_confirm(self):
        """
        
        """
        _logger.debug("confirmado finalização da Turma")
        self.turma_disciplina_id.write({
            'data_termino': self.data_termino,
           
            'state': 'aulas_encerradas',
        })
