# -*- coding: utf-8 -*-


from email.policy import default
from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatriculaDisciplina(models.Model):
    _name = "geracad.curso.matricula.disciplina"
    _description = "matricula de Disciplinas de Cursos"
    _check_company_auto = True
    _order = "aluno_id"

    
    _inherit = ['mail.thread']
    


    name = fields.Char("Cód. Matrícula", compute="_compute_name", store=True)
    
    company_id = fields.Many2one(
        'res.company', string="Unidade",required=True, default=lambda self: self.env.company
    )

    curso_matricula_id = fields.Many2one(
        'geracad.curso.matricula',
        string='Matricula',
        required=True
        )
    curso_matricula_codigo = fields.Char(
       
        related='curso_matricula_id.name',
        string='Matricula',
        
        readonly=True, 
        
        
        store=True
        )
    curso_nome = fields.Char( 
        related='curso_matricula_id.curso_turma_id.curso_id.name',
        string="Nome do curso",
        readonly=True,
        store=True
    )
    
    turma_disciplina_id = fields.Many2one(
        "geracad.curso.turma.disciplina",
        string='Turma Disciplina',
        required=True
        
        )
    periodo = fields.Integer(
        
        related='turma_disciplina_id.periodo',
        readonly=True,
      
        
        )
    disciplina_id = fields.Many2one(
        related='turma_disciplina_id.disciplina_id',
        readonly=True,
        store=True
        )
    

    e_pendencia = fields.Boolean("É pendencia", default=False, tracking=True)
    e_aproveitamento = fields.Boolean("É aproveitamento", default=False, tracking=True)

  


            
    
    nota = fields.One2many(string='Nota',comodel_name='geracad.curso.nota.disciplina',inverse_name='disciplina_matricula_id' )
    
    notas_disciplinas_count = fields.Integer(
        string='Disciplinas', 
        compute='_compute_notas_disciplinas',
            
        )
    
    
    def _compute_notas_disciplinas(self):
        for record in self:    
            record.notas_disciplinas_count = self.env["geracad.curso.nota.disciplina"].search(
                [('curso_matricula_id', '=', record.curso_matricula_id.id)],
                offset=0, limit=None, order=None, count=True)

    aluno_id = fields.Many2one(
        
        related = 'curso_matricula_id.aluno_id',
        string='Nome do Aluno',
        readonly=True,
        store=True,
        )   
    # aluno_nome = _id = fields.Many2one(
        
    #     related = 'curso_matricula_id.aluno_id.name',
    #     string='Nome do Aluno',
    #     readonly=True,
    #     store=True,
    #     )   
   
    data_matricula = fields.Date(
        string='Data Matrícula',
        default=fields.Date.context_today,
        tracking=True
    )
    data_conclusao = fields.Date(
        string='Data Conclusão',
        
       
        tracking=True,
    )

   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('inscrito', 'Inscrito'),
        ('trancado', 'Trancada'),
        ('abandono', 'Abandono'), 
        ('suspensa', 'Suspensa'), 
        ('cancelada', 'Cancelada'),
        ('expulso', 'Expulso'), 
        ('falecido', 'Falecido'),
        ('transferido', 'Transferido'),
        ('finalizado', 'Concluído'),
        
    ], string="Status", default="draft", readonly=False)



    active = fields.Boolean(default=True)
    
    _sql_constraints = [ ('curso_matricula_id_turma_disciplina_id_unique','UNIQUE(curso_matricula_id, turma_disciplina_id)','Aluno já matriculado nessa disciplina') ]

    @api.depends('curso_matricula_id')
    def _compute_name(self):
        for record in self:
            record.name = record.curso_matricula_id.name
    


    @api.model
    def create(self, vals):
        
        curso_matricula = self.env['geracad.curso.matricula'].search([('id', '=', vals['curso_matricula_id'] )])
        self = self.with_company(curso_matricula.company_id)

        vals['name'] = curso_matricula.name + " - " + curso_matricula.aluno_id.name
        vals['state'] = 'inscrito'
        
        result = super(GeracadCursoMatriculaDisciplina, self).create(vals)

        _logger.info("Criado Matricula")
        _logger.info(result)

        #criando as notas do aluno
        self.env['geracad.curso.nota.disciplina'].create(
             {
                 "company_id": result.company_id.id,
                 "disciplina_matricula_id": result.id,
                 "turma_disciplina_id": result.turma_disciplina_id.id
                

             }
             )



        return result
    
    """

            PRIVATE FUNCTIONS

    """
    
    def _finaliza_matricula_disciplina(self):
        self.write({
            'state':'finalizado'
        })

    def _reabre_matricula_disciplina(self):

        if self.curso_matricula_id.state  == 'inscrito':
            self.write({
                'state':'inscrito'
            })

    def _suspende_matricula_disciplina(self):
        self.write({
            'state':'suspensa'
        })

    def _cancela_matricula_disciplina(self):
        
       
           
        self.nota.write({
            'state':'cancelada',
            'situation' : 'CA',
        })
        self.write({
            'state':'cancelada'
        })
        
    def _tranca_matricula_disciplina(self):
        self.write({
            'state':'trancado'
        })
        if self.nota.state != 'concluida':
            if self.nota.situation == 'IN':
                self.nota.write({
                    'state':'concluida',
                    'situation' : 'TR',
                })
            else:
                self.nota.write({
                    'state':'concluida',  
                })

    def _set_data_conclusao_matricula_disciplina(self):
        data_hoje = date.today()
        self.write({'data_conclusao' : data_hoje})
        
    # def reativa_situation_notas(self):
    #     if self.nota.situation in  ['TR','AB']:
    #         self.nota.calcula_situation()
        
    def atualiza_frequencia_aulas(self):
        _logger.info("ATUALIZANDO FREQUENCIA DO ALUNO")
        '''
            Função que procura todas as aulas da turma de disciplina que o aluno está matriculado,
            e adiciona a frequencia, caso não tenha, com as faltas, calculando as faltas no diario final
            da turma disciplina.
        '''
        # PROCURA AS AULAS DA TURMA DISCIPLINA
        # VERIFICA SE ALUNO JÁ ESTAVA NA FREQUENCIA
        # SE NÃO COLOCA O ALUNO E COLOCA FALTA

        for rec in self:
            aulas_ids = self.env["geracad.curso.turma.disciplina.aulas"].search([
                ('turma_disciplina_id','=',rec.turma_disciplina_id.id)

                ])
            _logger.info("AULAS DA TURMA DISCIPLINA QUE O ALUNO ESTA MATRICULADO")
            _logger.info(aulas_ids)
            
            for aulas in aulas_ids:
                _logger.info(aulas.name)
                not_frequencia_ids = self.env['geracad.curso.turma.disciplina.aulas.frequencia'].search([
                    '&',
                    ('matricula_disciplina_id','not in', [rec.id]),
                    ('turma_aula_id','=', aulas.id)
                    
                    ])
                _logger.info('AULAS QUE O ALUNO NAO ESTAVA INSCRITO')
                _logger.info(not_frequencia_ids)

                for not_frequencia in not_frequencia_ids:

                    _logger.info("COLOCANDO ALUNO COM FALTA NESSA AULA")
                    _logger.info(not_frequencia)
                    frequencia = not_frequencia.create({
                        'matricula_disciplina_id': rec.id,
                        'turma_aula_id': aulas.id

                    })
                    _logger.info("QUANTIDADE DE FALTAS ADICIONADAS AO ALUNO")
                    _logger.info(frequencia.count_faltas)
                    frequencia.matricula_disciplina_id.nota.faltas += frequencia.count_faltas
                

    
    """

            BUTTON ACTIONS

    """

    def action_finaliza_matricula_disciplina(self):
        for rec in self:
            rec._set_data_conclusao_matricula_disciplina()
            rec._finaliza_matricula_disciplina()

    def action_reabrir_matricula_disciplina(self):
        for rec in self:
            rec._reabre_matricula_disciplina()

    def action_tranca_matricula_disciplina(self):
        for rec in self:
            if rec.state == 'draft' or rec.state == 'inscrito':
                rec._tranca_matricula_disciplina()

    def action_cancela_matricula_disciplina(self):
        for rec in self:
            if rec.state in ['draft','inscrito']:
                rec._cancela_matricula_disciplina()

    def action_suspende_matricula_disciplina(self):
        for rec in self:
            if rec.state == 'draft' or rec.state == 'inscrito':
                rec._suspende_matricula_disciplina()
             

    def action_go_notas_disciplinas(self):

        _logger.info("action open notas disciplinas")
        
        return {
            'name': _('Notas Disciplinas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.nota.disciplina',
            'domain': [('curso_matricula_id', '=', self.curso_matricula_id.id)],
            'context': {
                'default_curso_matricula_id': self.curso_matricula_id.id,
     
            }
        }
    

        

    
       