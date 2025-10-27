# © 20125 Afonso Carvalho AFR Soluções Inteligentes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoWizardPrintGrade(models.TransientModel):
    """
    Wizard para selecionar e imprimir a grade curricular de um curso.
    Permite ao usuário escolher o curso e qual versão da grade deseja visualizar.
    """
    _name = "geracad.curso.wizard.print.grade"
    _description = "Assistente para imprimir grade curricular do curso"

    # Campo para selecionar o curso
    curso_id = fields.Many2one(
        "geracad.curso", 
        string="Curso"
    )
    
    # Campo para selecionar a versão da grade curricular
    grade_versao = fields.Many2one(
        "geracad.curso.grade.versao",
        string="Versão da Grade",
        default=lambda self: self._default_grade_versao()
    )
    
    def _default_grade_versao(self):
        """
        Define a versão mais recente da grade como padrão.
        Se o curso vier do contexto, busca a versão mais recente daquele curso.
        """
        curso_id = self.env.context.get('default_curso_id')
        if curso_id:
            # Busca a versão mais recente (não obsoleta) do curso
            versao = self.env['geracad.curso.grade.versao'].search([
                ('curso_id', '=', curso_id),
                ('e_obsoleta', '=', False)
            ], order='data_inicio desc', limit=1)
            
            if versao:
                _logger.info("Versão padrão selecionada: %s", versao.name)
                return versao.id
        
        return False
    
    @api.onchange('curso_id')
    def _onchange_curso_id(self):
        """
        Quando o curso é alterado, seleciona automaticamente a versão mais recente
        e atualiza o domínio para mostrar apenas versões do curso selecionado.
        """
        if self.curso_id:
            # Busca a versão mais recente (não obsoleta) do curso selecionado
            versao = self.env['geracad.curso.grade.versao'].search([
                ('curso_id', '=', self.curso_id.id),
                ('e_obsoleta', '=', False)
            ], order='data_inicio desc', limit=1)
            
            if versao:
                self.grade_versao = versao.id
                _logger.info("Versão selecionada automaticamente: %s para curso %s", 
                           versao.name, self.curso_id.name)
            else:
                self.grade_versao = False
                _logger.warning("Nenhuma versão de grade encontrada para o curso %s", 
                              self.curso_id.name)
            
            return {
                'domain': {
                    'grade_versao': [('curso_id', '=', self.curso_id.id)]
                }
            }
        else:
            self.grade_versao = False
            return {
                'domain': {
                    'grade_versao': [('id', '=', False)]
                }
            }

    def action_confirm(self):
        """
        Ação executada ao clicar no botão Confirmar.
        Valida a seleção e chama o método de impressão.
        """
        self.ensure_one()
        
        # Log para debug
        _logger.info("=== DEBUG WIZARD ===")
        _logger.info("Curso ID: %s", self.curso_id)
        _logger.info("Curso ID value: %s", self.curso_id.id if self.curso_id else None)
        _logger.info("Grade Versao: %s", self.grade_versao)
        _logger.info("Grade Versao ID: %s", self.grade_versao.id if self.grade_versao else None)
        
        # Validações
        if not self.curso_id:
            raise UserError(_("Por favor, selecione um curso."))
        
        if not self.grade_versao:
            raise UserError(_("Por favor, selecione uma versão da grade curricular."))
        
        # Verifica se a versão pertence ao curso selecionado
        if self.grade_versao.curso_id.id != self.curso_id.id:
            raise UserError(_("A versão da grade selecionada não pertence ao curso escolhido."))
        
        _logger.info("Iniciando impressão de grade curricular do curso %s - Versão: %s", 
                     self.curso_id.name, self.grade_versao.name)
        
        # Gera o relatório passando a versão da grade selecionada
        return self.env.ref('geracad_curso.action_curso_grade_report')\
            .report_action(self.grade_versao)
       
