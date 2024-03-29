# -*- coding: utf-8 -*-

from ast import For
from email.policy import default

from odoo import models, fields, api, _
from datetime import date, datetime,time, timedelta

from babel.dates import format_datetime, format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

import logging

_logger = logging.getLogger(__name__)



class GeracadCursoTurmaDisciplinaAulas(models.Model):
    _name = "geracad.curso.turma.disciplina.aulas"
    _description = "Aulas da Turma de disciplina de Curso"
    _check_company_auto = True
    _order = 'hora_inicio_agendado DESC'

    
    _inherit = ['mail.thread']
    
    

    name = fields.Char("Assunto", 
    
    )

    company_id = fields.Many2one(
        'res.company',string="Unidade", required=True, default=lambda self: self.env.company
    )
    
    
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        required=True, 
        domain=[('state','=','aberta')],

        )
    hora_default = fields.Float()
    duration_default = fields.Integer()

    # @api.onchange("turma_disciplina_id" )
    # def onchange_turma_disciplina_id(self):
    #     if self.turma_disciplina_id.curso_turma_id:
    #         self.turma_curso_ids =  self.turma_disciplina_id.curso_turma_id 
                
    
        
  
    turma_curso_ids = fields.Many2one(
        "geracad.curso.turma",
        string='Turma Curso',
  
        related='turma_disciplina_id.curso_turma_id',

        )
    
   
    
    disciplina_id = fields.Many2one(
        string='Disciplina',
        related='turma_disciplina_id.disciplina_id',
        readonly=True,
        store=True
        )
        
    
    @api.depends('name', 'turma_disciplina_id')
    def name_get(self):
        result = []
        for record in self:
           
            name = '[' + str(record.turma_disciplina_id.disciplina_id.name) + '] ' + str(record.name)

           
            result.append((record.id, name))
        return result
    
        

    curso_id = fields.Many2one(
        string='Curso',
        related='turma_disciplina_id.curso_id',
        readonly=True,
        store=True
        )

    hora_inicio_agendado = fields.Datetime(
        string='Inicio Programado',
        
        #default= lambda self: datetime.utcnow().replace(hour=int(self.turma_disciplina_id.hora_inicio_padrao),minute=0,second=0) ,
        default=lambda self: self._default_hora_inicio_agendado(),
        tracking=True,
        required=True
    )
   
    @api.onchange('hora_inicio_agendado')
    def _onchange_hora_inicio_agendado(self):
        _logger.info(self.env.context)
        context = dict(self.env.context )
        if context.get('default_tempo_hora_aula_programado'):
            delta_hours = int(context['default_tempo_hora_aula_programado'])
        else:
            delta_hours = 3
        self.hora_termino_agendado = self.hora_inicio_agendado+timedelta(hours=delta_hours)


    def _default_hora_inicio_agendado(self):
        current_date = fields.Date.context_today(self.with_context(tz=self.env.user.tz))
        _logger.info(f"DT HOJE: {current_date}")
        _logger.info(f"turma: {self.turma_disciplina_id}")
        _logger.info(f"horapadrao: {self.turma_disciplina_id.hora_inicio_padrao}")

        if self.turma_disciplina_id.hora_inicio_padrao:
            current_time = time(int(self.turma_disciplina_id.hora_inicio_padrao),0,0)
            _logger.info(f"hora padrao: {current_time}")
            _logger.info(f"DT combinada: {datetime.combine(current_date, current_time)}")

            return datetime.combine(current_date, current_time)

        return current_date
    def atualiza_faltas(self):
        '''
            atualiza faltas na nota da turma disciplina
        '''
        notas = self.turma_disciplina_id.notas
        for nota in notas:
            nota.atualiza_faltas()
            


    @api.constrains('tempo_hora_aula_programado')
    def _check_tempo_hora_aula_programado(self):
        if self.tempo_hora_aula_programado < 1 or self.tempo_hora_aula_programado > 4:
            raise ValidationError(_('O tempo de aula tem que estar entre 1 a 4 horas.'))

    @api.constrains('hora_inicio_agendado','hora_termino_agendado')
    def _check_hora_inicio_agendado(self):  
        _logger.info("Verificando hora de inicio")
        for record in self:
            if record.hora_termino_agendado:
                if record.hora_termino_agendado <= record.hora_inicio_agendado :
                    raise ValidationError("Hora de inicio programada tem que ser antes da hora de término")

    hora_termino_agendado = fields.Datetime(
        string='Término Programado',     
        default= lambda self: datetime.now() +  relativedelta(hours=self.turma_disciplina_id.qtd_horas_aula_padrao),
        tracking=True,    
        required=True
    )

    tempo_hora_aula_programado = fields.Integer("Tempo Programado",compute="_compute_tempo_hora_aula_programado", 
    inverse='_inverse_tempo_hora_aula_programado'
    )
    
    def _inverse_tempo_hora_aula_programado(self):
        for rec in self:
            if rec.tempo_hora_aula_programado > 4:
                rec.tempo_hora_aula_programado = 4
            if rec.tempo_hora_aula_programado < 1: 
                rec.tempo_hora_aula_programado = 1
            rec.hora_termino_agendado = rec.hora_inicio_agendado + timedelta(hours=rec.tempo_hora_aula_programado)


    @api.depends("hora_termino_agendado","hora_inicio_agendado")
    def _compute_tempo_hora_aula_programado(self):
        for rec in self:
            if rec.hora_termino_agendado and rec.hora_inicio_agendado:
                rec.tempo_hora_aula_programado = (rec.hora_termino_agendado - rec.hora_inicio_agendado).total_seconds()/3600
                if(rec.tempo_hora_aula_programado < 0):
                    rec.tempo_hora_aula_programado = 3

    @api.onchange('tempo_hora_aula_programado')
    def onchange_tempo_hora_aula_programado(self):
        self._inverse_tempo_hora_aula_programado()

    hora_inicio = fields.Datetime(
        string='Inicio',
        tracking=True
    )

    
    hora_termino = fields.Datetime(
        string='Término',       
        tracking=True
    )
   
    tipo_de_aula = fields.Selection(string='Tipo', selection=[
        ('teorica', 'Teórica'),
        ('pratica', 'Prática'),
        ('teorica_pratica', 'Teórica e Prática'),
        ('avaliacao', 'Avaliação'),
        ], required=True)

    professor_id =  fields.Many2one(
    
        related='turma_disciplina_id.professor_id',
        readonly=True,
        store=True,
    
        )

    
    frequencia_ids = fields.One2many(
        string='Frequência',
        comodel_name='geracad.curso.turma.disciplina.aulas.frequencia',
        inverse_name='turma_aula_id',

    )
    
    
 
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('agendada', 'Agendada'),
        ('em_andamento', 'Em andamento'),
        ('concluida', 'Concluída'),      
        ('cancelada', 'Cancelada'),
        
    ], string="Status", default="agendada", tracking=True)

    sala_id = fields.Many2one(
        'geracad.curso.sala',
        string='Sala',
    )
    descricao = fields.Html("Descrição")
    
    active = fields.Boolean(default=True)
    
    
    
    def unlink(self):
        for rec in self:
            if rec.state not in ['agendada','draft']:
                raise ValidationError(_('Não é possível excluir uma aula que já está em andamento ou concluída.'))
                

        res = super().unlink()
    
        return res
    
    #usado na impressão do diário
    def get_diario_date(self):
        '''
            Função que retorna uma string da data para impressão do diário
            no formato: ex. São Luis-MA, 02 de agosto de 2022
        '''
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(self.data_encerramento,format="long",locale=locale)
        return   date_str

   


    #apaga os filtros que não serão possível fazer procura
    def get_fields_to_ignore_in_search(self): 
        
        return [ 'message_needaction',
           
            'create_date',
            'create_uid',
            'message_channel_ids',
            'message_attachment_count',
            'message_follower_ids',
            'message_has_error',
            'message_has_error_counter',
            'message_has_sms_error',
            'message_ids',
            'message_is_follower',
            'message_main_attachment_id',
            'message_needaction',
            'message_needaction_counter',
            'message_partner_ids',
            'message_unread',
            'message_unread_counter',
            'website_message_ids',
            'write_date',
            'write_uid',
            '__last_update',
            
            ]

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(GeracadCursoTurmaDisciplinaAulas, self).fields_get(allfields, attributes=attributes)
        _logger.info(res)
        for field in self.get_fields_to_ignore_in_search():

            if res.get(field):
                res[field]['searchable'] = False 
                res[field]['selectable'] = False 
                res[field]['sortable'] = False     
                res[field]['exportable'] = False 
        return res

    
    '''
        Retorna as matriculas disciplinas que estao inscritas ou suspensas
    '''

    def _get_matriculas_ativas(self):
        _logger.info("Pegando matriculas ativas")
        matricula_disciplina_ids = []
        matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([
                '&',
                ('turma_disciplina_id','=',self.turma_disciplina_id.id),
                ('state','in',['inscrito','suspensa'])

                ])
        _logger.info(matricula_disciplina_ids)
        return matricula_disciplina_ids

    '''
        Monta a lista de frequencia baseada nas matriculas ativas (inscritos, suspensos)
        colocando em default presenca para os inscritos e falta para os suspensos
    '''        
            

    def _monta_frequencia(self):
        _logger.info("Montando a frequencia dos alunos")
        tempo_hora_aula_teorico = 60*50
        for rec in self:

          
            matricula_disciplina_ids = rec._get_matriculas_ativas()
            hora_1 = True
            hora_2 = False
            hora_3 = False
            hora_4 = False
            frequencias_ids_write = []
            for matricula_disciplina in matricula_disciplina_ids:
                # se matricula tiver suspensa coloca falta
                if matricula_disciplina.state in ['suspensa','trancado','abandono']:
                    hora_1 = hora_2 = hora_3 = hora_4 = False
                elif rec.hora_termino_agendado and rec.hora_inicio_agendado:
                    hora_1 = True
                    tempo_hora_aula_programado = (rec.hora_termino_agendado - rec.hora_inicio_agendado).total_seconds()
                    if tempo_hora_aula_programado >= 2*tempo_hora_aula_teorico:
                        hora_2 = True
                    if tempo_hora_aula_programado >= 3*tempo_hora_aula_teorico:
                        hora_3 = True
                    if tempo_hora_aula_programado >= 4*tempo_hora_aula_teorico:
                        hora_4 = True
                else:
                    hora_1 = hora_2 = hora_3 = hora_4 = True
                
                frequencias_ids_write.append((0,0, {
                        'turma_aula_id': rec.id,
                        'matricula_disciplina_id': matricula_disciplina.id,
                        'hora_1': hora_1,
                        'hora_2': hora_2,
                        'hora_3': hora_3,
                        'hora_4': hora_4,
                        
                    })) 
                
            rec.write({
                    'frequencia_ids': frequencias_ids_write
                   
                })
    


    def _adiciona_frequencia_na_nota_disciplina(self):
        '''
            Função que soma a contagem de faltas da frequencia na nota de cada aluno
        '''
        _logger.info("Calculando e adicionando as faltas na turma")
        for rec in self:
            for frequencia in rec.frequencia_ids:
                frequencia.matricula_disciplina_id.nota.faltas += frequencia.count_faltas
    
    def _remove_frequencia_na_nota_disciplina(self):
        '''
            Função que conta as faltas da frequencia na nota de cada aluno
            e retira do diário as faltas.

        '''
        _logger.info("Calculando e removendo as faltas na turma")
        for rec in self:
            for frequencia in rec.frequencia_ids:
                frequencia.matricula_disciplina_id.nota.faltas -= frequencia.count_faltas

    def _delete_frequencia(self):
        '''
            Função apaga toda a lista de frequencia.

        '''
        _logger.info("Excluindo lista de frequencia")
        for rec in self:
            rec.write({
                'frequencia_ids' : [(5,0,0)],
            })
            rec.atualiza_faltas()
            
   
    def action_agendar(self):

        _logger.info("agendando")

        for rec in self:
            if rec.turma_disciplina_id.state not in ['draft', 'aberta','em_andamento']:
                raise ValidationError(_('Esta turma de disciplina está encerrada, suspensa ou cancelada'))

            if rec.state not in ['draft', 'agendada']:
                raise ValidationError(_('Esta aula já foi iniciada'))
            rec.write({
                'state': 'agendada',
            })

    def action_iniciar(self):
        _logger.info("iniciando")
        
        for rec in self:
            if rec.turma_disciplina_id.state not in ['draft', 'aberta','em_andamento']:
                raise ValidationError(_('Esta turma de disciplina está encerrada, suspensa ou cancelada'))
            if rec.state not in ['draft', 'agendada']:
                raise ValidationError(_('Esta aula já foi iniciada'))
            rec._monta_frequencia()
            rec.write({
                'state': 'em_andamento',
                'hora_inicio': fields.Datetime.now()
            }
               
            )

    def action_open_frequencia_view(self):
 
        

        if self._context['action'] == "agendar":
            self.action_agendar()
            return

        if self._context['action'] == "iniciar":
            self.action_iniciar()

        if self._context['action'] == "reiniciar":
            self.action_reiniciar()
       
            
            
        res_model = 'geracad.curso.turma.disciplina.aulas' 
        return {
            'name': ('Frequencia'),
            'view_type': 'form',
            'view_mode': 'form',
           # 'view_id': [view_id],
            'res_model': res_model, 
            'type': 'ir.actions.act_window',
            'context': {'default_id': self.id,'create': 0},
            'target': 'new',
            'res_id': self.id,
            'nodestroy': True,
            
        }

    def action_finalizar(self):
        _logger.info("finalizando")
        for rec in self:
            if rec.state in ['concluida']:
                raise ValidationError(_('Esta aula já foi concluída'))
            if rec.state not in ['em_andamento']:
                raise ValidationError(_('Esta aula deve ser iniciada primeiro'))
            if not rec.name:
                raise ValidationError(_('Digite o assunto da aula para poder finalizar.'))
            rec._adiciona_frequencia_na_nota_disciplina()
            rec.write({
                'state': 'concluida',
                'hora_termino': fields.Datetime.now()
            })
    def action_reiniciar(self):
        _logger.info("Reiniciando")
        for rec in self:
            _logger.info("STATE TURMA " + rec.turma_disciplina_id.state )
            if rec.turma_disciplina_id.state not in ['draft', 'aberta','em_andamento']:
                raise ValidationError(_('Esta turma de disciplina está encerrada, suspensa ou cancelada. Não é possível reiniciar lista de frequência'))
            
            if rec.state in ['draft','agendada']:
                raise ValidationError(_('Esta aula já está em '  + rec.state + '. Só aulas em andamento ou concluídas podem ser reiniciadas.'))
           
            if rec.state == 'concluida':
                rec._remove_frequencia_na_nota_disciplina()
            rec._delete_frequencia()
            
            rec.write({
                'state': 'agendada',
                'hora_inicio': None,
                'hora_termino': None,
            })

class GeracadCursoTurmaDisciplinaAulasFrequencia(models.Model):
    _name = "geracad.curso.turma.disciplina.aulas.frequencia"
    _description = "Frequencia das Aulas da Turma de disciplina de Curso"
    _check_company_auto = True

    company_id = fields.Many2one(
        'res.company',string="Unidade", required=True, default=lambda self: self.env.company
    )
    turma_aula_id = fields.Many2one(
        'geracad.curso.turma.disciplina.aulas',
        string='Aulas',
        )
    turma_disciplina_id = fields.Many2one(
        related='turma_aula_id.turma_disciplina_id',
        readonly=True,
        store=True
    )
    _sql_constraints = [
            (
                'constraint_turma_disciplina_id_matricula_disciplina_id_uniq_name',
                'unique(turma_disciplina_id,matricula_disciplina_id)',
                'Não pode ter duas vezes o mesmo aluno na frequencia'
            ),
        ]
    
    matricula_disciplina_id = fields.Many2one(
        "geracad.curso.matricula.disciplina",
        string="Matrícula Disciplina"
    )
    matricula_disciplina_id_state = fields.Selection(
        related='matricula_disciplina_id.state',
        string="Matrícula status"
    )
    curso_matricula_name = fields.Char(
      
        string='Matrícula',
        related='matricula_disciplina_id.curso_matricula_id.name',
        readonly=True,
        store=True
        )
    aluno_name = fields.Char(
     
        string='Aluno',
        related='matricula_disciplina_id.aluno_id.name',
        readonly=True,
        store=True
        )

    
    def write(self, values):
        res = super().write(values)
        self.turma_aula_id.atualiza_faltas()
        return res
    
    hora_1 = fields.Boolean("1ª hora", default=False)
    @api.onchange('hora_1')
    def onchange_hora_1(self):
        if self.turma_aula_id.tempo_hora_aula_programado > 1:
            self.hora_2 = self.hora_1
        if self.turma_aula_id.tempo_hora_aula_programado > 2:
            self.hora_3 = self.hora_1
        if self.turma_aula_id.tempo_hora_aula_programado > 3:
            self.hora_4 = self.hora_1


    hora_2 = fields.Boolean("2ª hora", default=False)
    hora_3 = fields.Boolean("3ª hora", default=False)
    hora_4 = fields.Boolean("4ª hora", default=False)

    count_faltas =  fields.Integer(
        string='Faltas',compute="_compute_faltas"
    )




    @api.depends('hora_1','hora_2','hora_3','hora_4')
    def _compute_faltas(self):
        
        for rec in self:
            qtd_horario = self._calcula_hora_aula( rec.turma_aula_id.hora_inicio_agendado,rec.turma_aula_id.hora_termino_agendado)
            _logger.info("qtd horario")
            _logger.info(qtd_horario)
            faltas = 0
            soma_presenca = 0
           
            if rec.hora_1:
                soma_presenca += 1 
            if rec.hora_2:
                soma_presenca += 1 
            if rec.hora_3:
                soma_presenca += 1 
            if rec.hora_4:
                soma_presenca += 1 

            _logger.info("numero de presencas")
            _logger.info(qtd_horario)
            if soma_presenca < qtd_horario:
                faltas = qtd_horario - soma_presenca
                
            _logger.info("qtd de faltas")
            _logger.info(faltas)
            rec.count_faltas = faltas
           
            
    

    def _calcula_hora_aula(self, hora_ini, hora_fim):
        '''
            Recebe Datatime de inicio e de fim
            e retorna quantidade de hora aula
            
        '''
        _logger.info("HORA INICIO")
        _logger.info(hora_ini)
        _logger.info("HORA FIM")
        _logger.info(hora_fim)
        tempo_hora_aula = 50 # tempo da hora aula em minutos
        max_hora_aula = 4 # valor maximo hora aula
        tempo_de_aula =  ((hora_fim -  hora_ini).seconds // 60)  # tempo de aula em minutos
        _logger.info("TEMPO DE AULA")
        _logger.info(tempo_de_aula)
        hora_aula = tempo_de_aula//tempo_hora_aula
        _logger.info("HORA AULA CALCULADA")
        _logger.info(hora_aula)
        if hora_aula >= max_hora_aula:
            hora_aula = max_hora_aula
        if hora_aula < 0:
            hora_aula = 0
        _logger.info("HORA AULA RETORNADA")
        _logger.info(hora_aula)
        return hora_aula

       


    

        

    
       