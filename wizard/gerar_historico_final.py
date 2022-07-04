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
    
    data_conclusao = fields.Date(
        string="Data Conclusão do Curso",
        default=fields.Date.context_today,
    )
    
    disciplina_faltantes_id = fields.One2many(
       "geracad.curso.disciplinas.faltantes.historico.final", 
       inverse_name="gerar_historico_final_id",
       readonly=True, string="Disciplinas Faltantes",
       domain=[('concluida','=',0)]
    )
    disciplina_concluidas_id = fields.One2many(
       "geracad.curso.disciplinas.faltantes.historico.final", 
       inverse_name="gerar_historico_final_id",
       readonly=True, string="Disciplinas Concluídas",
       domain=[('concluida','=',1)]
    )


    
    
    def _gera_nota_historico_final_aluno(self):
        _logger.info("GERANDO NOTAS DO HISTÓRICO FINAL")
        nota_disciplina_ids = self.env['geracad.curso.nota.disciplina'].search([
            '&',
            ('curso_matricula_id','=',self.matricula_id.id),
            ('situation','in',['AM','AP','EA']),
            ])
        for nota_disciplina in nota_disciplina_ids:
            _logger.info(nota_disciplina.disciplina_matricula_id)
            self.env['geracad.curso.nota.disciplina.historico.final'].create({
                'disciplina_matricula_id': nota_disciplina.disciplina_matricula_id.id,
                'periodo': nota_disciplina.periodo,
                'faltas': nota_disciplina.faltas,
                'nota_1': nota_disciplina.nota_1,
                'nota_2': nota_disciplina.nota_2,
                'final': nota_disciplina.final,
                'media': nota_disciplina.media,
                'carga_horaria': nota_disciplina.turma_disciplina_carga_horaria,
                'situation': nota_disciplina.situation,
                'state': 'concluida'

            }
            )

   

    def action_confirm(self):
        """
        
        """
        _logger.debug("Confirmado Geração de Histórico Final")
        if len(self.disciplina_faltantes_id) > 0:
            raise UserError(_('O histórico final só poderá ser gerado caso o aluno tenha todas as disciplinas do curso concluídas e aprovadas.'))
        self._gera_nota_historico_final_aluno()
            
        
    

class GeracadCursoDisciplinasFaltantesHistoricoFinal(models.TransientModel):
    _name = "geracad.curso.disciplinas.faltantes.historico.final"
    _description = "Disciplinas Faltantes histórico Final"

  
    gerar_historico_final_id = fields.Many2one(
       "geracad.curso.gerar.historico.final",
     
        )
        
    disciplina_id =  fields.Many2one(
       
        "geracad.curso.disciplina", string="Disciplinas"
    )
    concluida = fields.Boolean(
       
         string="Concluída"
    )
    
