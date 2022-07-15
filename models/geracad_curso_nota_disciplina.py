# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date
from odoo.exceptions import ValidationError
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
        store=True,
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
        group_operator="avg",
    )
    
    periodo = fields.Integer(
        string='periodo',
        compute="_compute_periodo",
        store=True,
        
        
    )
    gerado_historico_final = fields.Boolean("Histórico final?")
    
    def _disciplina_periodo_procura_matricula_grade(self):
        disciplina_id = self.turma_disciplina_id.disciplina_id
        grade_version_id = self.curso_matricula_id.curso_grade_version
        grade_lines = self.env['geracad.curso.grade'].search([
            '&',
            ('curso_grade_version','=',grade_version_id),
            ('disciplina_id','=',disciplina_id)
            ])
        for grade in grade_lines:
            return grade.periodo
        return 1
        
        
   
    #@api.depends('disciplina_matricula_id','curso_matricula_id')
    def _compute_periodo(self):
        
        for record in self:
            if record.turma_disciplina_id.disciplina_id.e_estagio:
                record.periodo = 0
            if self.turma_disciplina_id.periodo:
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
        ('FA', 'FA'),
        ], default='IN', string="Situação",tracking=True)


   
    # aluno_nome = _id = fields.Many2one(
        
    #     related = 'curso_matricula_id.aluno_id.name',
    #     string='Nome do Aluno',
    #     readonly=True,
    #     store=True,
    #     )   
   
   
    
   
    
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('atualizando', 'Em atualização'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    ], string="Status", default="draft", tracking=True)
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_disciplina_matricula_id_turma_disciplina_id_unique','UNIQUE(disciplina_matricula_id, turma_disciplina_id)','Aluno já com notas nessa turma disciplina') ]
   
    @api.constrains('faltas')
    def _check_faltas(self):  
        for record in self:
            if record.faltas < 0 or record.faltas > record.turma_disciplina_id.carga_horaria:
                raise ValidationError("As faltas devem estar entre 0 e " + str(record.turma_disciplina_id.carga_horaria) )
    
    @api.constrains('nota_1')
    def _check_nota_1(self):  
        for record in self:
            if record.nota_1 < 0 or record.nota_1 > 10.0:
                raise ValidationError("A nota 1 deve estar entre 0 e 10")
    
    @api.constrains('nota_2')
    def _check_nota_2(self):  
        for record in self:
            if record.nota_2 < 0 or record.nota_2 > 10.0:
                raise ValidationError("A nota 2 deve estar entre 0 e 10")
    
    @api.constrains('final')
    def _check_final(self):  
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
        

    @api.onchange('nota_1','nota_2','final','faltas')
    def _onchange_categ_id(self):    
        _logger.debug("mudou nota")
        
        for record in self:
            if record.state != 'concluida':
                if record.turma_disciplina_id.e_aproveitamento:
                    record.situation = 'EA'
                else:
                    if record.faltas > 0.25*record.turma_disciplina_id.carga_horaria:
                        record.situation = 'RF'
                    else:
                        media = self._calcula_media(record.nota_1,record.nota_2, record.final)
                        if media >= 5:
                            if (record.nota_1 + record.nota_2) >= 14:
                                record.situation = 'AM'
                            else:
                                record.situation = 'AP'
                        else:
                            record.situation = 'RC'

    """

            BUTTON ACTIONS

    """
    def action_lancar_nota(self):    
        _logger.debug("Nota Lançada")
        self.write({
            'state': 'concluida'
        })
        

