# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
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
   
    def _lancando_notas(self):
        matriculas_disciplina =  self.env["geracad.curso.matricula.disciplina"].search(
                [('turma_disciplina_id', '=', self.turma_disciplina_id.id)],
                offset=0, limit=None, order=None)
        for matricula in matriculas_disciplina:
            if matricula.state in ['inscrito','draft']:
                matricula.nota.calcula_situation()
    
    
    def _aulas_estao_concluidas(self):
        for aula in self.turma_disciplina_id.aulas:
            if aula.state not in ['concluida','cancelada']:
                raise ValidationError(_('Todas as aulas devem estar com o status de concluída.'))





    def action_confirm(self):
        """
        
        """
        _logger.debug("confirmado finalização da Turma")
        self._aulas_estao_concluidas()
        self._lancando_notas()
        
        self.turma_disciplina_id.write({
            'data_termino': self.data_termino,
            'state': 'aulas_encerradas',
        })
