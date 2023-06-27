# -*- coding: utf-8 -*-

import warnings
from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError, Warning
import logging

_logger = logging.getLogger(__name__)

#TODO
# Fazer botão de finalizar notas
# fazer estatísticas de notas (com média por curso, melhor nota etc)

class GeracadCursoNotaDisciplina(models.Model):
    _name = "geracad.curso.nota.disciplina"
    _description = "Notas de Disciplinas de Cursos"
    _check_company_auto = True
    _order = 'aluno_nome'
  
    _inherit = ['mail.thread']
  
    name = fields.Char("Nome")
    
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    disciplina_matricula_id = fields.Many2one(
        'geracad.curso.matricula.disciplina',
        string='Matricula Disciplina',
        required=True
        )
   

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string="Matricula Curso",
        
        related='disciplina_matricula_id.curso_matricula_id',
        readonly=True,
        store=True
        
        )
    
    curso_matricula_codigo = fields.Char("Código",
        related='curso_matricula_id.name', 
        store=True,
        readonly=True
         )
         
    aluno_nome = fields.Char(
       
        string="Nome do Aluno",
        
        related='disciplina_matricula_id.curso_matricula_id.aluno_id.name',
        readonly=True,
        store=True
        
        )
    disciplina_matricula_state = fields.Selection(
       
        string="Status",
        
        related='disciplina_matricula_id.state',
        readonly=True,
        store=True
    )
    
    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string="Turma Curso",
        
        related='disciplina_matricula_id.curso_matricula_id.curso_turma_id',
        readonly=True,
        store=True
        
        )
    curso_id = fields.Many2one(
        'geracad.curso',
        
        related='disciplina_matricula_id.curso_matricula_id.curso_turma_id.curso_id',
        readonly=True,
        store=True
        
        )

    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        
        related='disciplina_matricula_id.turma_disciplina_id',
        readonly=True,
        store=True,
        ) 
    turma_disciplina_data_abertura = fields.Date(
        string='Data de Abertura',
        related='disciplina_matricula_id.turma_disciplina_id.data_abertura',
        readonly=True,
        store=True,
        )
    turma_disciplina_data_inicio = fields.Date(
        string='Data de início',
        related='disciplina_matricula_id.turma_disciplina_id.data_inicio',
        readonly=True,
        store=True,
        )
    turma_disciplina_data_encerramento = fields.Date(
        string='Data de encerramento',
        related='disciplina_matricula_id.turma_disciplina_id.data_encerramento',
        readonly=True,
        store=True,
        )
    turma_disciplina_data_previsao_termino = fields.Date(
        string='Previsão de Término',
        related='disciplina_matricula_id.turma_disciplina_id.data_previsao_termino',
        readonly=True,
        store=True,
        )
    turma_disciplina_carga_horaria = fields.Integer(
        string='Carga Horária',
        related='disciplina_matricula_id.turma_disciplina_id.carga_horaria',
        readonly=True,
        store=False,
        )
    professor_id = fields.Many2one(
        "res.partner",
        string='Professor',
        
        related='disciplina_matricula_id.turma_disciplina_id.professor_id',
        readonly=True,
        store=True,
        
        
        
        )
    disciplina_id = fields.Many2one(
        "geracad.curso.disciplina",
        related='turma_disciplina_id.disciplina_id',
        
        readonly=True, 
        
        string='Disciplina',      
        store=True    
        )

    faltas = fields.Integer(
        string='Faltas',
        default=0,
        tracking=True,
        group_operator="sum",
    )

   
    
    # abonos_faltas_ids = fields.One2many(colmodel ="geracad.curso.nota.disciplina.abono.falta",
    #                                     string= 'Histórico Abonos', inverse_name = "nota_id")
    
    faltas_lista_frequencia = fields.Integer(
        string='Faltas freq.',
        default=0,
        # store=True,
        group_operator="sum",
        #compute="_calcula_frequencia_atual_na_turma_disciplina"

    )
    faltas_abonadas = fields.Integer(
        string='Abonadas',
        default=0,
        store=True,
        group_operator="sum",
        compute="_calcula_faltas_abonadas"
        

    )
    def atualiza_faltas(self):
        for rec in self:
            rec._calcula_frequencia_atual_na_turma_disciplina()
            rec._calcula_faltas_abonadas()
    
    @api.depends('faltas','faltas_lista_frequencia','faltas_abonadas')
    def _calcula_faltas_abonadas(self):
        faltas_saldo = 0
        for rec in self:
            faltas_saldo = rec.faltas_lista_frequencia - rec.faltas
            if faltas_saldo < 0:
                faltas_saldo =0
            rec.faltas_abonadas = faltas_saldo
            
            

    @api.depends('faltas','faltas_lista_frequencia','faltas_abonadas')
    def _calcula_frequencia_atual_na_turma_disciplina(self):
        _logger.info("Calculando faltas de aluno na turma de disciplina")
        for rec in self:
            #pegando todas as frequencias da matricula do aluno nesta turma de disciplina
            frequencias_da_matricula_ids = rec.env['geracad.curso.turma.disciplina.aulas.frequencia'].search([
                        ('turma_disciplina_id', '=',rec.turma_disciplina_id.id ), 
                        ('matricula_disciplina_id', '=', rec.disciplina_matricula_id.id) 
                        ], offset=0, limit=None, order=None, count=None)
            soma_faltas = 0
            for frequencia in frequencias_da_matricula_ids:
                soma_faltas += frequencia.count_faltas
            
            rec.faltas_lista_frequencia = soma_faltas
          
            


    periodo = fields.Integer(
        string='periodo',
        compute="_compute_periodo",
        store=True,
        
        
    )
    gerado_historico_final = fields.Boolean("Histórico final?")
    
    def _disciplina_periodo_procura_matricula_grade(self):
        disciplina_id = self.turma_disciplina_id.disciplina_id
        grade_version_id = self.curso_matricula_id.curso_grade_version
        periodo = 1
        grade_lines = self.env['geracad.curso.grade'].search([
            '&',
            ('curso_grade_version','=',grade_version_id),
            ('disciplina_id','=',disciplina_id)
            ])
        for grade in grade_lines:
            if grade.periodo != 0:
                periodo = grade.periodo
        return periodo
        
    
   
    #@api.depends('disciplina_matricula_id','curso_matricula_id')
    def _compute_periodo(self):
        '''
            Calcula periodo da nota
            - Caso seja Estágio a disciplina o periodo é zero
            - Caso seja outra disciplina
            - E o período da turma da disciplina seja diferente de zero, o periodo da nota
                é igual ao da turma da disciplina
            - Caso nenhum dos anteriores cacula pela grade da matrícula do aluno

        '''
        
        for record in self:
            if record.turma_disciplina_id.disciplina_id.e_estagio:
                record.periodo = 0
            else:
                if self.turma_disciplina_id.periodo != 0:
                    record.periodo = self.turma_disciplina_id.periodo
                else:
                    record.periodo = record._disciplina_periodo_procura_matricula_grade()

    
    nota_1 = fields.Float(group_operator="avg", tracking=True)
    nota_2 = fields.Float(group_operator="avg",tracking=True)
    final = fields.Float(group_operator="avg",tracking=True)
    media = fields.Float("Média", compute="_compute_media", 
    store=True,tracking=True,group_operator="avg",
    )
    situation = fields.Selection([
        ('AM', 'AM'), # aprovado por media
        ('AP', 'AP'), # aprovado por final
        ('RC', 'RC'), # reprovado por conteudo
        ('RF', 'RF'), # repovado por Falta
        ('IN', 'IN'), # inscrito
        ('CA', 'CA'), # cancelado
        ('TR', 'TR'), # trancado
        ('AB', 'AB'), # abandono
        ('EA', 'EA'), # estudos aproveitados
        ('FA', 'FA'), # falecido
        ('EX', 'EX'), # expulso
        ('SU', 'SU'), # Suspenso pelo financeiro
        ], default='IN', string="Situação",tracking=True)

   
    
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('atualizando', 'Em atualização'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ], string="Status", default="draft", tracking=True)
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_disciplina_matricula_id_turma_disciplina_id_unique','UNIQUE(disciplina_matricula_id, turma_disciplina_id)','Aluno já com notas nessa turma disciplina') ]
    
    def _validationStatus(self):
        if(self.state not in ['draft','inscrito']):
            raise ValidationError('O aluno ' + self.aluno_nome + ' está ' + self.disciplina_matricula_id.state + ' e não pode ser alterado a sua nota' )


    @api.constrains('faltas')
    def _check_faltas(self):  
        #self._validationStatus()
        for record in self:
            if record.faltas < 0 :
                record.faltas = 0
    
    @api.constrains('nota_1')
    def _check_nota_1(self):  
        self._validationStatus()
        for record in self:
            if record.nota_1 < 0 or record.nota_1 > 10.0:
                raise ValidationError("A nota 1 deve estar entre 0 e 10")
    
    @api.constrains('nota_2')
    def _check_nota_2(self):  
        self._validationStatus()
        for record in self:
            if record.nota_2 < 0 or record.nota_2 > 10.0:
                raise ValidationError("A nota 2 deve estar entre 0 e 10")
    
    @api.constrains('final')
    def _check_final(self):  
        self._validationStatus()
        for record in self:
            if record.final < 0 or record.final > 10.0:
                raise ValidationError("A nota Final deve estar entre 0 e 10")

    @api.depends('nota_1', 'nota_2','final')
    def _compute_media(self):
        for record in self:
            record.media = self._calcula_media(record.nota_1,record.nota_2,record.final)

    def _calcula_media(self,n1,n2,final):
        media = (n1 + n2)/2
        if(media < 7):
            if final > 0:
               media = (media + final)/2

        return media
    
    def _esta_aprovado_por_notas(self):
        media = (self.nota_1 + self.nota_2)/2
      
        if(media < 7):
            if self.final > 0:
                media = (media + self.final)/2
                if media < 5:
                    return False
                else:
                    return True
            else:
                return False
        else:
            return True
            
        

    def calcula_situation(self):
        
        for record in self:
            status_matricula_disciplina = record.disciplina_matricula_id.state
           
            if status_matricula_disciplina in  ['inscrito','draft']:
                if record.turma_disciplina_id.e_aproveitamento:
                    record.situation = 'EA'
                else:
                    if record.faltas > 0.25*record.turma_disciplina_id.disciplina_id.carga_horaria:
                        record.situation = 'RF'
                    else:
                        media = self._calcula_media(record.nota_1,record.nota_2, record.final)
                        if(record.final > 0): 
                            if media >= 5:
                                    record.situation = 'AP'
                            else:
                                record.situation = 'RC'                                
                        else:
                            if(media >= 7):
                                record.situation = 'AM'
                            else:
                                record.situation = 'RC'
            elif status_matricula_disciplina == 'trancado':
                record.situation = 'TR'
            elif status_matricula_disciplina == 'abandono':
                record.situation = 'AB'
            elif status_matricula_disciplina == 'suspensa':
                record.situation = 'SU'
            elif status_matricula_disciplina == 'cancelada':
                record.situation = 'CA'
            elif status_matricula_disciplina == 'expulso':
                record.situation = 'EX'
            elif status_matricula_disciplina == 'falecido':
                record.situation = 'FA'
            elif status_matricula_disciplina == 'transferido':
                record.situation = 'TR'
            

    @api.onchange('nota_1','nota_2','final','faltas')
    def _onchange_notas_faltas(self):     
        for record in self:
            record.faltas_abonadas = record.faltas_lista_frequencia - record.faltas
            if record.state != 'concluida':
                record.calcula_situation()
                if record.situation == 'RF':
                    if record._esta_aprovado_por_notas():
                        return {
                            'value': {'faltas': record.turma_disciplina_carga_horaria*0.25},
                            'warning': {'title': "Warning", 'message': "O aluno está reprovado por falta, mas poderá ser aprovado por conteúdo. O sistema irá abonar as faltas automaticamente do aluno"},
                        }
                                    
                            

    
    
    def write(self, values):
        """
            Update all record(s) in recordset, with new value comes as {values}
            return True on success, False otherwise
    
            @param values: dict of new values to be set
    
            @return: True on success, False otherwise
        """
       
        # if(self.state in ['concluida']):
        #     raise ValidationError(_('Esta nota já foi lançada e não pode ser alterada'))
        # if(self.state in ['cancelada']):
        #     raise ValidationError(_('O  aluno está cancelado e não pode ser alterado a sua nota'))
        # if(self.disciplina_matricula_id.state not in ['draft','inscrito']):
        #     raise ValidationError(_('O aluno ' + self.aluno_nome + ' está ' + self.disciplina_matricula_id.state + ' e não pode ser alterado a sua nota'))
        
        result = super(GeracadCursoNotaDisciplina, self).write(values)
    
        return result
    

    """

            BUTTON ACTIONS

    """
    def action_lancar_nota(self):    
        _logger.debug("Nota Lançada")
        self.write({
            'state': 'concluida'
        })
    def action_atualiza_situation(self):
        self.calcula_situation()
    
    def action_reabrir_nota(self):    
        _logger.debug("Nota Reaberta para edição")
        self.write({
            'state': 'draft'
        })

class NotasDialog(models.TransientModel):
    _name = 'geracad.curso.nota.dialog'
    
    name = fields.Char('Name')
    description = fields.Text('Description')
    nota_id =  fields.Many2one(
        "geracad.curso.nota.disciplina",
     
        )
    
    def action_confirm(self):
        # Lógica para confirmar a ação
        #
        # Ajeitar a nota do cara
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        # Lógica para cancelar a ação
        return {'type': 'ir.actions.act_window_close'}
        
# class GeracadCursoNotaDisciplinaAbonoFalta(models.Model):
#     _name = "geracad.curso.nota.disciplina.abono.falta"
#     _description = "Abono de faltas das Disciplinas de Cursos"
#     _check_company_auto = True
   
  
#     _inherit = ['mail.thread']

#     nota_id =  fields.Many2one(
#         'geracad.curso.nota.disciplina',
#         string='Nota',
#         )
#     faltas_abonadas  = fields.Integer(
#         string='Faltas Abonadas',
#     )
#     justificativa  = fields.Char(
#         string='Justificativa',
#     )
    

