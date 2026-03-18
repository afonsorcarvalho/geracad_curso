# © 2025 Afonso Carvalho AFR Soluções Inteligentes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class CopiarGradeWizard(models.TransientModel):
    """
    Wizard para copiar uma versão da grade curricular de um curso.
    Permite duplicar toda a estrutura da grade com suas disciplinas.
    """
    _name = "copiar.grade.wizard"
    _description = "Assistente para copiar versão da grade curricular"

    # Curso de origem (pode ser diferente do curso de destino)
    curso_origem_id = fields.Many2one(
        "geracad.curso",
        string="Curso de Origem",
        required=True,
        help="Curso de onde será copiada a grade"
    )
    
    # Versão da grade a ser copiada
    grade_versao_origem = fields.Many2one(
        "geracad.curso.grade.versao",
        string="Versão da Grade a Copiar",
        required=True,
        help="Selecione a versão da grade que deseja copiar"
    )
    
    # Curso de destino (para onde será copiada a grade)
    curso_destino_id = fields.Many2one(
        "geracad.curso",
        string="Curso de Destino",
        required=True,
        help="Curso para onde será copiada a grade"
    )
    
    # Data de início da nova versão
    data_inicio = fields.Date(
        string="Data de Início da Nova Versão",
        required=True,
        default=fields.Date.context_today,
        help="Data de início da nova versão da grade"
    )
    
    # Opção para marcar a origem como obsoleta
    marcar_origem_obsoleta = fields.Boolean(
        string="Marcar Versão Original como Obsoleta",
        default=False,
        help="Se marcado, a versão original será marcada como obsoleta após a cópia"
    )

    @api.onchange('curso_origem_id')
    def _onchange_curso_origem_id(self):
        """
        Atualiza o domínio da versão de origem quando o curso de origem muda.
        Limpa a versão selecionada quando trocar de curso.
        """
        self.grade_versao_origem = False
        
        if self.curso_origem_id:
            return {
                'domain': {
                    'grade_versao_origem': [('curso_id', '=', self.curso_origem_id.id)]
                }
            }
        return {
            'domain': {
                'grade_versao_origem': [('id', '=', False)]
            }
        }

    def action_copiar_grade(self):
        """
        Executa a cópia da grade curricular.
        Cria uma nova versão com todas as disciplinas da versão original.
        Permite copiar de um curso para outro.
        """
        self.ensure_one()
        
        # Validações
        if not self.curso_origem_id:
            raise UserError(_("Selecione o curso de origem."))
        
        if not self.curso_destino_id:
            raise UserError(_("Selecione o curso de destino."))
        
        if not self.grade_versao_origem:
            raise UserError(_("Selecione uma versão da grade para copiar."))
        
        if not self.data_inicio:
            raise UserError(_("Informe a data de início da nova versão."))
        
        # Verifica se já existe uma versão com a mesma data de início no curso de destino
        versao_existente = self.env['geracad.curso.grade.versao'].search([
            ('curso_id', '=', self.curso_destino_id.id),
            ('data_inicio', '=', self.data_inicio)
        ])
        
        if versao_existente:
            raise UserError(_(
                "Já existe uma versão da grade com a data de início %s no curso de destino.\n"
                "Por favor, escolha outra data."
            ) % self.data_inicio.strftime('%d/%m/%Y'))
        
        _logger.info("Iniciando cópia da grade curricular: %s para o curso %s", 
                    self.grade_versao_origem.name, self.curso_destino_id.name)
        
        # Cria a nova versão da grade no curso de destino
        nova_versao = self.env['geracad.curso.grade.versao'].create({
            'curso_id': self.curso_destino_id.id,
            'data_inicio': self.data_inicio,
            'e_obsoleta': False,
        })
        
        _logger.info("Nova versão criada: %s", nova_versao.name)
        
        # Copia todas as disciplinas da grade original
        disciplinas_copiadas = 0
        for grade_item in self.grade_versao_origem.grade_ids:
            if not grade_item.e_excluida:  # Só copia disciplinas não excluídas
                self.env['geracad.curso.grade'].create({
                    'version_grade_id': nova_versao.id,
                    'curso_id': self.curso_destino_id.id,
                    'disciplina_id': grade_item.disciplina_id.id,
                    'periodo': grade_item.periodo,
                    'modulo': grade_item.modulo,
                    'sequence': grade_item.sequence,
                    'e_obrigatoria': grade_item.e_obrigatoria,
                    'e_excluida': False,
                })
                disciplinas_copiadas += 1
        
        _logger.info("Total de disciplinas copiadas: %d de %s para %s", 
                    disciplinas_copiadas, self.curso_origem_id.name, self.curso_destino_id.name)
        
        # Marca a versão original como obsoleta se solicitado
        if self.marcar_origem_obsoleta:
            self.grade_versao_origem.write({'e_obsoleta': True})
            _logger.info("Versão original marcada como obsoleta: %s", self.grade_versao_origem.name)
        
        # Mensagem personalizada dependendo se é cópia entre cursos diferentes
        if self.curso_origem_id.id == self.curso_destino_id.id:
            mensagem = _(
                'Grade curricular copiada com sucesso!\n\n'
                'Curso: %s\n'
                'Nova versão: %s\n'
                'Total de disciplinas: %d'
            ) % (self.curso_destino_id.name, nova_versao.name, disciplinas_copiadas)
        else:
            mensagem = _(
                'Grade curricular copiada com sucesso!\n\n'
                'De: %s (%s)\n'
                'Para: %s (%s)\n'
                'Total de disciplinas: %d'
            ) % (self.curso_origem_id.name, self.grade_versao_origem.name,
                 self.curso_destino_id.name, nova_versao.name, disciplinas_copiadas)
        
        # Exibe mensagem de sucesso
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sucesso!'),
                'message': mensagem,
                'type': 'success',
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                },
            }
        }

