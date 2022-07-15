# -*- coding: utf-8 -*-

from ast import For
from odoo import models, fields, api, _
from datetime import date
from babel.dates import format_datetime, format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

import logging

_logger = logging.getLogger(__name__)



class GeracadCursoTurmDisciplina(models.Model):
    _name = "geracad.curso.turma.disciplina"
    _description = "Turmas de disciplina de Curso"
    _check_company_auto = True

    
    _inherit = ['mail.thread']
    
    

    name = fields.Char("Código")
    company_id = fields.Many2one(
        'res.company',string="Unidade", required=True, default=lambda self: self.env.company
    )

    disciplina_id = fields.Many2one(
        'geracad.curso.disciplina',
        string='Disciplina',
        required=True, 
   
        
        )
  

    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Curso Turma',
        )
    curso_grade_version = fields.Many2one(
        string='Versão Grade',
        
        related='curso_turma_id.curso_grade_version',
        readonly=True,
        store=True
       
        )
   
    
    # curso_turma_nome = fields.Char("Código Curso", 
    #     related='curso_turma_id.name',
    #     readonly=True,
    #     store=True
    # )
    curso_id = fields.Many2one(
        string = "Curso", 
        related='curso_turma_id.curso_id',
        readonly=True,
        store=True
    )
    
    #TODO
    #mudar esse periodo da turma para default em vez de compute
    periodo = fields.Integer(
        string = "Periodo", 
        default = 1, 
    )

    @api.depends('periodo')
    def onchange_periodo(self):
        _logger.info("MUDANDO O PERIODO DAS NOTAS")
        for nota in self.notas:
            res = nota.write({
                'periodo': self.periodo
            })
            _logger.info(res)
    

    #TODO
    #mudar esse periodo da turma para default em vez de compute
    carga_horaria = fields.Integer(
        string = "Carga horária", 
        
       
        
        
    )
   
    @api.onchange('disciplina_id','curso_turma_id')
    def onchange_disciplina_id_curso_id(self):
            self.carga_horaria = self.disciplina_id.carga_horaria
            if self.curso_turma_id:
                grade_id = self.env['geracad.curso.grade'].search([
                ('disciplina_id', '=', self.disciplina_id.id  ),
                ('curso_id', '=', self.curso_turma_id.curso_id.id  )], 
                offset=0, limit=1, order=None, count=False)
                for grade in grade_id:
                    self.periodo = grade.periodo

    
    #TODO
    # verificar essa funcao se esta correta
    # @api.depends('curso_turma_id','disciplina_id') 
    # def _compute_dados_grade(self):
    #     for record in self:
    #         grade_id = self.env['geracad.curso.grade'].search([
    #             ('disciplina_id', '=', record.disciplina_id.id  ),
    #             ('curso_id', '=', record.curso_id.id  )], 
    #             offset=0, limit=1, order=None, count=False)
            
    #         record.periodo = grade_id.periodo
    #         record.carga_horaria = record.disciplina_id.carga_horaria
        
  
   
    matricula_aberta = fields.Boolean(string="Matrícula Aberta", default=True)
    
    data_abertura = fields.Date(
        string='Data Abertura',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    data_inicio = fields.Date(
        string='Inicio das aulas',
        default=fields.Date.context_today,
        track_visibility='true'
    )
    data_termino = fields.Date(
        string='Término das aulas',
        
        track_visibility='true'
    )
   
    
    data_previsao_termino = fields.Date(
        string='Previsão de término',
        default= lambda self: date.today() +  relativedelta(months=4),
        track_visibility='true'
       
    )

    data_encerramento = fields.Date(
        string='Data Encerramento',
        track_visibility='true'
    )
     
    professor_id =  fields.Many2one(
        'res.partner',
        string='Professor',
        required=True,
        domain=[('e_professor','=', True)]
        )
   
    vagas = fields.Integer(
        string='Vagas',track_visibility='true'
    )
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('aberta', 'Matrícula Aberta'),
        ('aulas_encerradas', 'Aulas Encerradas'),
        ('encerrada', 'Disciplina Encerrada'),
        ('suspensa', 'Matrícula Suspensa'), 
        ('em_andamento', 'Em andamento'), 
        ('cancelada', 'Cancelada'),
        
    ], string="Status", default="draft", track_visibility='true')

    sala_id = fields.Many2one(
        'geracad.curso.sala',
        string='Sala',
    )

    carga_horaria = fields.Integer("Carga Horária")
    e_pendencia = fields.Boolean("É pendência")
    e_aproveitamento = fields.Boolean("É aproveitamento")

    alunos_count = fields.Integer(
        string='Alunos', 
        compute='_compute_alunos_count',
            
        )
    notas = fields.One2many('geracad.curso.nota.disciplina', 'turma_disciplina_id')
    active = fields.Boolean(default=True)
    

    @api.constrains('carga_horaria')
    def _check_carga_horaria(self):  
        for record in self:
            if record.carga_horaria <= 0:
                raise ValidationError("A carga horária tem que ser maior que zero")

    @api.constrains('periodo')
    def _check_periodo(self):  
        for record in self:
            if record.periodo < 0:
                raise ValidationError("O período não pode ser menor que zero")



    def write(self, vals):
        # Agregar codigo de validacion aca
        
        res = super(GeracadCursoTurmDisciplina, self).write(vals)      
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([
            ('turma_disciplina_id','=',self.id)
            ])
        for nota in nota_ids:
            nota.write({
                'periodo': self.periodo
            })

        return res
    
    #usado na impressão do diário
    def get_diario_date(self):
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(self.data_encerramento,format="long",locale=locale)
        return   date_str

    #usado na impressão da ata
    def get_ano_semestre(self,tipo):
        if tipo == "semestre":
            if(self.data_abertura.month > 6):
                return '2º'
            else:
                return '1º'
        if tipo == "ano":
            return self.data_abertura.year


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
        res = super(GeracadCursoTurmDisciplina, self).fields_get(allfields, attributes=attributes)
        _logger.info(res)
        for field in self.get_fields_to_ignore_in_search():

            if res.get(field):
                res[field]['searchable'] = False 
                res[field]['selectable'] = False 
                res[field]['sortable'] = False     
                res[field]['exportable'] = False 
        return res

    def _compute_alunos_count(self):
        for record in self:    
            record.alunos_count = self.env["geracad.curso.matricula.disciplina"].search(
                [('turma_disciplina_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)

    
    
    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('New')) == _('New'):
            seq_date = None
        vals['name'] = self._gera_codigo_turma(vals) or _('New')
        vals['state'] = 'aberta'
        
        
        result = super(GeracadCursoTurmDisciplina, self).create(vals)
       
        return result
    
    def action_ajeita_periodo_ch_notas(self):
        '''
            Atualiza os periodos das notas atualizando para o período da turma disciplina
            utilizado em acoes agendadas
        '''
        _logger.info('AJEITANDO O PERIODO E A CARGA HORÁRIA DAS NOTAS')
        notas = self.env["geracad.curso.nota.disciplina"].search([])
                 
        for nota in notas:
            _logger.info('ajeitando nota')
            _logger.info(nota)
            nota._compute_periodo()


    def action_adiciona_alunos_turma_curso(self):
        _logger.debug("ADICIONANDO ALUNOS PELA TURMA CURSOS")
        _logger.debug(self.curso_turma_id.name)
        _logger.debug(self.name)
        self.message_post(body="Atualizado Lista de Alunos da disciplina!!")
       
        if self.curso_turma_id:
            _logger.debug("ADICIONADA A TURMA NO FORMULARIO")
            _logger.debug(self.curso_turma_id.name)
            #pega todos os alunos inscritos na turma do curso desta turma de disciplina
            matriculas_cursos_alunos = self.env['geracad.curso.matricula'].search([('curso_turma_id','=',self.curso_turma_id.id)])
            _logger.debug("MATRICULAS DE CURSOS ENCONTRADAS:")
            _logger.debug(matriculas_cursos_alunos)
           
            
            for matricula_curso in matriculas_cursos_alunos:     
                _logger.debug(matricula_curso.name)

                if matricula_curso.state == 'inscrito': 
                    _logger.debug("PROCURANDO SE MATRICULA JA ESTA ADICIONADA")
                    
                    matriculas_disciplinas_alunos = self.env['geracad.curso.matricula.disciplina'].search([
                       
                        '&',
                        ('turma_disciplina_id','=',self.id),
                        ('state','=','inscrito'),
                   
                    ])  
                    _logger.debug(matriculas_disciplinas_alunos)
                    ids_matriculas_cursos_alunos = list(map(lambda x: x.curso_matricula_id.id,matriculas_disciplinas_alunos))
                    _logger.debug(ids_matriculas_cursos_alunos)
                    if matricula_curso.id not in ids_matriculas_cursos_alunos:
                        _logger.debug("MATRICULANDO ALUNO")
                        _logger.debug("ADICIONANDO MATRICULA: " + str(matricula_curso.name))
                        self.env['geracad.curso.matricula.disciplina'].create({
                            'curso_matricula_id': matricula_curso.id,
                            'turma_disciplina_id': self.id,
                            'state': 'inscrito'
                        })
                    else:
                         _logger.debug("ALUNO JA MATRICULADO")

            
    
    @api.depends('name', 'disciplina_id')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.name + '] ' + record.disciplina_id.name
            result.append((record.id, name))
        return result
    
    #TODO
    # Verificar essa função que não está funcionando direito

    # @api.model
    # def name_search(self, name, args=None, operator='=ilike', limit=100):
    #     args = args or []
    #     domain = []
    #     if name:
    #         domain = [
    #             '|', ('name', '=ilike', name), ('disciplina_id', operator, name)
    #         ]
            
    #     records = self.search(domain + args, limit=limit)
    #     return records.name_get()
    
    
    
    
    def _gera_codigo_turma(self,vals):
        """
            Gera o codigo da turma de cursos pegando o codigo da unidade, o codigo do curso, o ano que foi criada a turma, 
            qual o turno MAT=3, VES=2, NOT=1 e um número sequencial
        """
        date_now = date.today()
        _logger.info("Ano ")
        _logger.info(date_now.strftime("%y"))

        company = self.env['res.company'].search([('id', '=', vals['company_id'])])
        _logger.info(company.name)
        disciplina = self.env['geracad.curso.disciplina'].search([('id', '=', vals['disciplina_id'] )])
        _logger.info(disciplina.name)
        
        codigo_turma = ''
        codigo_turma += disciplina.codigo + "."
        codigo_turma += date_now.strftime("%y%m")+"."
        codigo_turma += self._get_number_sequencial(codigo_turma)
        _logger.info(codigo_turma)
        return codigo_turma

    

    def _get_number_sequencial(self, codigo_turma):

        _logger.info('PROCURANDO NOME DE TURMA:')
        _logger.info(codigo_turma)
        turmas = self.env['geracad.curso.turma.disciplina'].search([('name', '=like', codigo_turma+"%")], order="name asc")
        
        if len(turmas) == 0:
            _logger.info('NENHUMA TURMA ENCONTRADA')
            return "01"
        _logger.info('TURMAS ENCONTRADAS')
        for turma in turmas:
            _logger.info('TURMAS ENCONTRADAS')
            _logger.info(turma.name)
            _logger.info(turma.name[-2:])
            number_sequencial_string = turma.name[-2:]
            number_sequencial = int(number_sequencial_string)+1
        resultado_string ="{:02d}"
        return resultado_string.format(number_sequencial)
    
    
    def action_corrige_periodo_CH(self):    
        '''
            Corrige erro no banco de dados antigo
            Coloca periodo e carga_horaria da turma de discicplina
            chamado com acoes agendadas
        '''
        _logger.info("Corrigindo periodo e CH de turma disciplinas")
        res = self.env["geracad.curso.turma.disciplina"].search([('curso_turma_id.name','=','XX22301')])
        
        
        for rec in res:
            _logger.info(rec.name)
            

            grade_rec = self.env["geracad.curso.grade"].search([('disciplina_id','=', rec.disciplina_id.id)], limit=1)
            if len(grade_rec) > 0:
                _logger.info(grade_rec[0].version_grade_id.name)
                periodo = grade_rec[0].periodo
            else:
                periodo = 1
            
            result = rec.write({
                'carga_goraria': rec.disciplina_id.carga_horaria,
                'periodo': periodo
            } )
            _logger.info(result)
    
    """

            BUTTON ACTIONS

    """

    def action_go_alunos_disciplinas(self):
        _logger.info("action open alunos disciplinas")

        return {
            'name': _('Alunos Matriculados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
               
            }
        }
    def action_go_notas_disciplinas(self):
        _logger.info("action open alunos disciplinas")

        return {
            'name': _('Notas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.nota.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
                
                'expand': True,
                'editable': "bottom",
            }
        }


    def action_suspender_turma_disciplina(self):
        self.write({
            'state': 'suspensa',
            'matricula_aberta': False,

        })

    def _encerra_notas_turma_disciplina(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        for nota in nota_ids:
            nota.action_lancar_nota()

    def _cancela_notas_turma_disciplina(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        for nota in nota_ids:
            nota.write({
                'state':'cancelada',
                'situation': 'CA'
            })

    def _set_data_encerramento_turma_disciplina(self):
        data_hoje = date.today()
        self.write({'data_encerramento' : data_hoje})
    
    def _finaliza_matricula_turma_disciplina(self):
        matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([('turma_disciplina_id','=',self.id)])
        for matricula_disciplina in matricula_disciplina_ids:
            matricula_disciplina.action_finaliza_matricula_disciplina()
    
    def _cancela_matricula_turma_disciplina(self):
        matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([('turma_disciplina_id','=',self.id)])
        matricula_disciplina_ids.action_cancela_matricula_disciplina()



    def action_finalizar_aulas(self):
        dummy, act_id = self.env["ir.model.data"].sudo().get_object_reference(
            "geracad_curso", "action_geracad_curso_finalizar_aula"
        )
        vals = self.env["ir.actions.act_window"].sudo().browse(act_id).read()[0]
        vals["context"] = {
           
           
            "default_turma_disciplina_id": self.id,
            
        }
        return vals



    def action_encerrar_turma_disciplina(self):
        self._encerra_notas_turma_disciplina()
        self._finaliza_matricula_turma_disciplina()
        self._set_data_encerramento_turma_disciplina()
        self.write({
            'state': 'encerrada',
            'matricula_aberta': False,
            })
    
    def action_cancelar_turma_disciplina(self):
        self._cancela_notas_turma_disciplina()
        self._cancela_matricula_turma_disciplina()
        self.write({
            'state': 'cancelada',
            'matricula_aberta': False,
            })

    def action_abrir_turma_disciplina(self):
        self.write({
            'state': 'aberta',
            'matricula_aberta': True,
            })

        

    
       