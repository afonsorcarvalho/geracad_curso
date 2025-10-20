# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class GeracadCursoTurmaHorario(models.Model):
    """
    Modelo para armazenar os horários das turmas de disciplinas dos cursos.
    Permite definir em quais dias da semana e horários específicos cada disciplina é ministrada.
    """
    _name = "geracad.curso.turma.horario"
    _description = "Horários das Turmas de Disciplinas"
    _check_company_auto = True
    

    # Herança de funcionalidades de rastreamento de mensagens
    _inherit = ['mail.thread']

    # Campos básicos
    name = fields.Char(
        string="Código do Horário",
       
    )

    @api.model
    def create(self, vals):
        
        now = datetime.now()
        ano_mes = f"{now.year}{now.month:02d}"
       
        
        curso_turma = self.env['geracad.curso.turma'].search([('id', '=', self.env.context.get('default_curso_turma_id') )],limit=1)
        if curso_turma:
            _logger.info("curso turma encontrado")
            vals['name'] = f"{curso_turma.name}/{ano_mes}"
        else:
            _logger.info("curso turma não encontrado")
            vals['name'] = f"{ano_mes}"
       

        result = super(GeracadCursoTurmaHorario, self).create(vals)

        return result
    
  
            
   
    company_id = fields.Many2one(
        'res.company',
        string="Unidade",
        required=True,
        default=lambda self: self.env.company
    )

    # Relacionamento com a turma do curso (relacionado através da turma de disciplina)
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Turma do Curso',
      
    )

    # Relacionamento com o curso (relacionado através da turma)
    curso_id = fields.Many2one(
        'geracad.curso',
        string='Curso',
        related='curso_turma_id.curso_id',
        readonly=True,
        store=True
    )
    todos_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        string='Todos os Horários'
    )

    segunda_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '0')],
        string='Horários - Segunda'
    )

    terca_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '1')],
        string='Horários - Terça'
    )

    quarta_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '2')],
        string='Horários - Quarta'
    )

    quinta_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '3')],
        string='Horários - Quinta'
    )

    sexta_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '4')],
        string='Horários - Sexta'
    )

    sabado_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '5')],
        string='Horários - Sábado'
    )

    domingo_horarios_ids = fields.One2many(
        'geracad.curso.turma.horario.linha',
        'horario_id',
        domain=[('dia_semana', '=', '6')],
        string='Horários - Domingo'
    )

    # Campo para ativar/desativar o horário
    active = fields.Boolean(
        string='Ativo',
        default=True,
        tracking=True,
        help="Marque para desativar este horário"
    )

    # Campo para observações/notas sobre o horário
    observacoes = fields.Text(
        string='Observações',
        help="Observações adicionais sobre este horário"
    )
    

    

   

    def _get_dia_semana_display(self):
        """
        Retorna o nome do dia da semana formatado
        """
        return dict(self._fields['dia_semana'].selection)[self.dia_semana] if self.dia_semana else ''

    def _get_hora_formatada(self, hora_float):
        """
        Converte hora em formato float para string formatada (HH:MM)
        """
        if hora_float is not False:
            hora_int = int(hora_float)
            minuto_int = int((hora_float - hora_int) * 60)
            return f"{hora_int:02d}:{minuto_int:02d}"
        return ""

    # @api.model
    # def name_get(self):
    #     """
    #     Personaliza a exibição do nome do registro
    #     """
    #     result = []
    #     for record in self:
    #         if record.disciplina_id and record.dia_semana:
    #             dia_nome = record._get_dia_semana_display()
    #             hora_inicio = record._get_hora_formatada(record.hora_inicio)
    #             name = f"[{record.disciplina_id.name}] {dia_nome} {hora_inicio}"
    #         else:
    #             name = record.name or "Novo Horário"
    #         result.append((record.id, name))
    #     return result


class GeracadCursoTurmaHorarioLinha(models.Model):
    _name = "geracad.curso.turma.horario.linha"
    _description = "Linhas dos Horários das Turmas de Disciplinas"
    _check_company_auto = True
    _order = "disciplina_id, dia_semana, hora_inicio"

    _inherit = ['mail.thread']
    
    horario_id = fields.Many2one(
        'geracad.curso.turma.horario',
        string='Horário',
        required=True,
        ondelete='cascade'
    )
    
    disciplina_id = fields.Many2one(
        'geracad.curso.disciplina',
        string='Disciplina',
        required=True,
        ondelete='cascade'
    )
    
    dia_semana = fields.Selection([
        ('0', 'Segunda-feira'),
        ('1', 'Terça-feira'),
        ('2', 'Quarta-feira'),
        ('3', 'Quinta-feira'),
        ('4', 'Sexta-feira'),
        ('5', 'Sábado'),
        ('6', 'Domingo')
    ], string='Dia da Semana', required=True)
    
    professor_id = fields.Many2one(
        'res.partner',
        domain=[('e_professor','=', True)],
        string="Professor",
        required=True
    )
    sala_id = fields.Many2one(
        'geracad.curso.sala',
        string="Sala",
        required=True
    )
    
    
    hora_inicio = fields.Float(
        string='Hora de Início',
        required=True,
        help="Hora de início no formato decimal (ex: 19.0 para 19:00, 19.5 para 19:30)"
    )
    
    hora_termino = fields.Float(
        string='Hora de Término',
        required=True,
        help="Hora de término no formato decimal (ex: 22.0 para 22:00, 22.5 para 22:30)"
    )
    
    @api.onchange('hora_inicio', 'hora_termino')
    def _onchange_horarios(self):
        """
        Validação no lado do cliente: alerta quando horário de término é menor ou igual ao de início
        """
        if self.hora_inicio and self.hora_termino:
            if self.hora_termino <= self.hora_inicio:
                # Formata as horas para exibição
                hora_inicio_str = '%02d:%02d' % (int(self.hora_inicio), int((self.hora_inicio % 1) * 60))
                hora_termino_str = '%02d:%02d' % (int(self.hora_termino), int((self.hora_termino % 1) * 60))
                
                return {
                    'warning': {
                        'title': _('Atenção: Horário Inválido!'),
                        'message': _(
                            'O horário de término (%s) deve ser posterior ao horário de início (%s).\n\n'
                            'Por favor, corrija os horários antes de salvar.'
                        ) % (hora_termino_str, hora_inicio_str)
                    }
                }
  
    @api.constrains('hora_inicio', 'hora_termino')
    def _check_horarios(self):
        """
        Valida se o horário de término é posterior ao horário de início
        """
        for record in self:
            try:
                if record.hora_termino <= record.hora_inicio:
                    raise ValidationError(_("O horário de término deve ser posterior ao horário de início."))
            except Exception as e:
                _logger.error("Erro na validação de horários: %s", str(e))
                raise ValidationError(_("Erro ao validar horários: %s") % str(e))

    @api.constrains('disciplina_id', 'dia_semana', 'hora_inicio', 'hora_termino', 'horario_id')
    def _check_conflito_horario(self):
        """
        Verifica se não há conflito de horários para a mesma turma/disciplina no mesmo horário
        """
        for record in self:
            try:
                # Só verifica se está ativo
                if not hasattr(record, 'active') or not record.active:
                    continue
                    
                # Verifica se tem o horario_id (registro pai)
                if not record.horario_id:
                    continue
                
                # Busca outros horários ativos para o mesmo horario_id (mesmo período/turma)
                # que tenham conflito de professor, sala ou disciplina no mesmo dia/horário
                conflitos = self.search([
                    ('id', '!=', record.id),
                    ('horario_id', '=', record.horario_id.id),
                    ('dia_semana', '=', record.dia_semana),
                    ('active', '=', True),
                    '|',
                    # Conflito: novo horário inicia dentro de um horário existente
                    '&', ('hora_inicio', '<=', record.hora_inicio), ('hora_termino', '>', record.hora_inicio),
                    # Conflito: novo horário termina dentro de um horário existente
                    '&', ('hora_inicio', '<', record.hora_termino), ('hora_termino', '>=', record.hora_termino)
                ])
                
                if conflitos:
                    # Verifica conflitos específicos
                    mensagens = []
                    for conflito in conflitos:
                        if conflito.disciplina_id == record.disciplina_id:
                            mensagens.append(_("A disciplina '%s' já está agendada neste horário.") % record.disciplina_id.name)
                        if conflito.professor_id == record.professor_id:
                            mensagens.append(_("O professor '%s' já está alocado neste horário.") % record.professor_id.name)
                        if conflito.sala_id == record.sala_id:
                            mensagens.append(_("A sala '%s' já está ocupada neste horário.") % record.sala_id.name)
                    
                    if mensagens:
                        raise ValidationError("\n".join(set(mensagens)))
                        
            except ValidationError:
                # Re-raise ValidationError para que seja exibido ao usuário
                raise
            except Exception as e:
                # Captura outros erros e loga
                _logger.error("Erro na validação de conflito de horários: %s", str(e))
                raise ValidationError(_("Erro ao validar conflito de horários: %s") % str(e))