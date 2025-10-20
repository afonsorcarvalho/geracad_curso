# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CopiarHorarioWizard(models.TransientModel):
    """
    Wizard para copiar horários de disciplinas de outro horário existente.
    Copia apenas as disciplinas, dias da semana e horários, permitindo que
    o usuário ajuste professores e salas posteriormente.
    """
    _name = 'copiar.horario.wizard'
    _description = 'Wizard para Copiar Horários de Disciplinas'

    horario_origem_id = fields.Many2one(
        'geracad.curso.turma.horario',
        string='Copiar Horários De',
        required=True,
        help="Selecione o horário de onde deseja copiar as disciplinas"
    )
    
    horario_destino_id = fields.Many2one(
        'geracad.curso.turma.horario',
        string='Para o Horário',
        readonly=True,
        help="Horário atual onde os dados serão copiados"
    )
    
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Turma',
        related='horario_destino_id.curso_turma_id',
        readonly=True
    )
    
   
    
    # Campo removido - sempre substitui todos os horários
    # substituir_existentes sempre = True
    
    copiar_professores = fields.Boolean(
        string='Copiar Professores',
        default=True,
        help="Se marcado, copia também os professores atribuídos"
    )
    
    copiar_salas = fields.Boolean(
        string='Copiar Salas',
        default=True,
        help="Se marcado, copia também as salas atribuídas"
    )
    
    quantidade_linhas = fields.Integer(
        string='Quantidade de Horários',
        compute='_compute_quantidade_linhas',
        readonly=True
    )
    
    preview_linhas = fields.Html(
        string='Prévia dos Horários',
        compute='_compute_preview_linhas',
        readonly=True
    )

    @api.depends('horario_origem_id')
    def _compute_quantidade_linhas(self):
        """Calcula a quantidade de linhas de horários que serão copiadas"""
        for wizard in self:
            if wizard.horario_origem_id:
                wizard.quantidade_linhas = len(wizard.horario_origem_id.todos_horarios_ids)
            else:
                wizard.quantidade_linhas = 0

    @api.depends('horario_origem_id')
    def _compute_preview_linhas(self):
        """Gera uma prévia HTML dos horários que serão copiados"""
        for wizard in self:
            if not wizard.horario_origem_id or not wizard.horario_origem_id.todos_horarios_ids:
                wizard.preview_linhas = '<p style="color: #999; font-style: italic;">Nenhum horário para copiar.</p>'
                continue
            
            # Agrupa por dia da semana
            dias_semana = {
                '0': 'Segunda-feira',
                '1': 'Terça-feira',
                '2': 'Quarta-feira',
                '3': 'Quinta-feira',
                '4': 'Sexta-feira',
                '5': 'Sábado',
                '6': 'Domingo'
            }
            
            html = '<div style="max-height: 300px; overflow-y: auto;">'
            html += '<table class="table table-sm table-bordered" style="font-size: 12px;">'
            html += '<thead style="background-color: #f0f2f5;"><tr>'
            html += '<th>Dia</th><th>Horário</th><th>Disciplina</th>'
            if wizard.copiar_professores:
                html += '<th>Professor</th>'
            if wizard.copiar_salas:
                html += '<th>Sala</th>'
            html += '</tr></thead><tbody>'
            
            # Ordena por dia da semana e hora de início
            linhas_ordenadas = wizard.horario_origem_id.todos_horarios_ids.sorted(
                key=lambda l: (int(l.dia_semana), l.hora_inicio)
            )
            
            for linha in linhas_ordenadas:
                hora_inicio = '%02d:%02d' % (int(linha.hora_inicio), int((linha.hora_inicio % 1) * 60))
                hora_termino = '%02d:%02d' % (int(linha.hora_termino), int((linha.hora_termino % 1) * 60))
                
                html += '<tr>'
                html += f'<td>{dias_semana.get(linha.dia_semana, "")}</td>'
                html += f'<td>{hora_inicio} - {hora_termino}</td>'
                html += f'<td>{linha.disciplina_id.name}</td>'
                if wizard.copiar_professores:
                    html += f'<td>{linha.professor_id.name if linha.professor_id else "-"}</td>'
                if wizard.copiar_salas:
                    html += f'<td>{linha.sala_id.name if linha.sala_id else "-"}</td>'
                html += '</tr>'
            
            html += '</tbody></table></div>'
            wizard.preview_linhas = html

    @api.model
    def default_get(self, fields_list):
        """Define valores padrão ao abrir o wizard"""
        res = super(CopiarHorarioWizard, self).default_get(fields_list)
        
        # Obtém o horário atual do contexto
        active_id = self.env.context.get('active_id')
        if active_id:
            res['horario_destino_id'] = active_id
        
        return res

    def action_copiar_horarios(self):
        """
        Ação principal: copia os horários do horário de origem para o horário de destino
        """
        self.ensure_one()
        
        if not self.horario_origem_id:
            raise UserError(_('Por favor, selecione um horário de origem.'))
        
        if not self.horario_destino_id:
            raise UserError(_('Horário de destino não identificado.'))
        
        if self.horario_origem_id == self.horario_destino_id:
            raise UserError(_('O horário de origem não pode ser o mesmo que o horário de destino.'))
        
        if not self.horario_origem_id.todos_horarios_ids:
            raise UserError(_('O horário de origem não possui horários cadastrados para copiar.'))
        
        try:
            # PASSO 1: LIMPAR - Remove TODOS os horários existentes primeiro
            linhas_antigas = self.env['geracad.curso.turma.horario.linha'].search([
                ('horario_id', '=', self.horario_destino_id.id)
            ])
            
            quantidade_removida = 0  # Inicializa sempre
            
            if linhas_antigas:
                quantidade_removida = len(linhas_antigas)
                linhas_antigas.unlink()
                # Força o flush das operações de delete no banco de dados
                #self.env.cr.flush()
                _logger.info(
                    f"LIMPEZA: {quantidade_removida} horários removidos do horário "
                    f"{self.horario_destino_id.name} (ID: {self.horario_destino_id.id})"
                )
            else:
                _logger.info(f"LIMPEZA: Nenhum horário existente para remover")
            
            # PASSO 2: PREPARAR - Prepara os dados para criação
            linhas_para_criar = []
            for linha_origem in self.horario_origem_id.todos_horarios_ids:
                nova_linha = {
                    'horario_id': self.horario_destino_id.id,
                    'disciplina_id': linha_origem.disciplina_id.id,
                    'dia_semana': linha_origem.dia_semana,
                    'hora_inicio': linha_origem.hora_inicio,
                    'hora_termino': linha_origem.hora_termino,
                }
                
                # Copia professor se marcado
                if self.copiar_professores and linha_origem.professor_id:
                    nova_linha['professor_id'] = linha_origem.professor_id.id
                
                # Copia sala se marcado
                if self.copiar_salas and linha_origem.sala_id:
                    nova_linha['sala_id'] = linha_origem.sala_id.id
                
                linhas_para_criar.append(nova_linha)
            
            # PASSO 3: CRIAR - Cria as novas linhas após limpeza completa
            novas_linhas = self.env['geracad.curso.turma.horario.linha'].create(linhas_para_criar)
            # Força o flush das operações de insert no banco de dados
            #self.env.cr.flush()
            
            _logger.info(
                f"CÓPIA CONCLUÍDA: {len(linhas_para_criar)} horários copiados de "
                f"{self.horario_origem_id.name} para {self.horario_destino_id.name}"
            )
            
            # Mensagem de sucesso detalhada
            message = _(
                'Horários substituídos com sucesso!\n\n'
                '✓ %d horários removidos\n'
                '✓ %d horários copiados\n'
                '✓ De: %s\n'
                '✓ Para: %s'
            ) % (
                quantidade_removida,
                len(linhas_para_criar),
                self.horario_origem_id.name,
                self.horario_destino_id.name
            )
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sucesso!'),
                    'message': message,
                    'type': 'success',
                    'sticky': False,
                    'next': {
                        'type': 'ir.actions.act_window_close',
                    }
                }
            }
            
        except ValidationError as ve:
            # Erros de validação do modelo (conflitos, etc)
            raise UserError(
                _('Erro ao copiar horários:\n\n%s\n\n'
                  'Verifique se não há conflitos de horários, professores ou salas.') % str(ve)
            )
        except Exception as e:
            _logger.error(f"Erro ao copiar horários: {str(e)}")
            raise UserError(
                _('Erro inesperado ao copiar horários:\n\n%s\n\n'
                  'Verifique o log do sistema para mais detalhes.') % str(e)
            )

