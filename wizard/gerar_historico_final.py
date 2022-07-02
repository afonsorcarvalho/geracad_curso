# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoGerarHistoricoFinal(models.TransientModel):
    _name = "geracad.curso.gerar.historico.final"
    _description = "Assistente de Finalizar aulas de Turmas de Disciplinas"

  
    matricula_id = fields.Many2one(
        "geracad.curso.matricula",
        string='matricula',
        )

    disciplina_faltantes_id =  fields.One2many(
       "geracad.curso.disciplinas.faltantes.historico.final", 
       inverse_name="gerar_historico_final_id",
       readonly=True, string="Disciplinas Faltantes"
    )
    

   

    def action_confirm(self):
        """
        
        """
        _logger.debug("confirmado finalização da Turma")
        self.turma_disciplina_id.write({
            'data_termino': self.data_termino,  
           
            'state': 'aulas_encerradas',
        })

class GeracadCursoDisciplinasFaltantesHistoricoFinal(models.TransientModel):
    _name = "geracad.curso.disciplinas.faltantes.historico.final"
    _description = "Disciplinas Faltantes histórico Final"

  
    gerar_historico_final_id = fields.Many2one(
       "geracad.curso.gerar.historico.final",
     
        )
        
    disciplina_id =  fields.Many2one(
       
        "geracad.curso.disciplina", string="Disciplinas"
    )
    
