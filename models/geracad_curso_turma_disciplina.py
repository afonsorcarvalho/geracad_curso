# -*- coding: utf-8 -*-


import json
from re import search
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

    color_calendar = fields.Integer(
        string='Cor calendario',
    )

    disciplina_id = fields.Many2one(
        'geracad.curso.disciplina',
        string='Disciplina',
        required=True,     
        
        )
    
    tipo = fields.Selection(
        string='Tipo de Turma',
        selection=[('presencial', 'Presencial'), ('a_distancia', 'A Distância')],
        default = 'presencial',
    )
    
    domain_disciplina_id = fields.Char(
        compute="_compute_disciplina_id_domain",
        readonly=True,
        store=False,
    )
   
    
    @api.depends('curso_turma_id')
    def _compute_disciplina_id_domain(self):
        for rec in self:
            domain_disciplina = []
            if self.curso_turma_id and self.curso_turma_id.curso_grade_version:
                grade_ids = self.env["geracad.curso.grade"].search([("version_grade_id","=",self.curso_turma_id.curso_grade_version.id)])
                domain_disciplina = list(map(lambda x: x.disciplina_id.id, grade_ids))
                if grade_ids:
                    domain_disciplina = [('id', 'in', domain_disciplina)]
                        
                

            
            rec.domain_disciplina_id = json.dumps(domain_disciplina)



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
        tracking=True
    )
    data_inicio = fields.Date(
        string='Inicio das aulas',
        default=fields.Date.context_today,
        tracking=True
    )
    data_termino = fields.Date(
        string='Término das aulas',
        
        tracking=True
    )
   
    
    data_previsao_termino = fields.Date(
        string='Previsão de término',
        default= lambda self: date.today() +  relativedelta(months=4),
        tracking=True
       
    )

    data_encerramento = fields.Date(
        string='Data Encerramento',
        tracking=True
    )
     
    professor_id =  fields.Many2one(
        'res.partner',
        string='Professor',
        required=True,
        domain=[('e_professor','=', True)]
        )
   
    vagas = fields.Integer(
        string='Vagas',tracking=True
    )
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('aberta', 'Matrícula Aberta'),
        ('aulas_encerradas', 'Aulas Encerradas'),
        ('encerrada', 'Disciplina Encerrada'),
        ('suspensa', 'Matrícula Suspensa'), 
        ('em_andamento', 'Em andamento'), 
        ('cancelada', 'Cancelada'),
        
    ], string="Status", default="draft", tracking=True)

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
    aulas_count = fields.Integer(
        string='aulas', 
        compute='_compute_aulas_count',
            
        )
    aulas = fields.One2many('geracad.curso.turma.disciplina.aulas', 'turma_disciplina_id')

    
    total_horas_aulas_ministradas = fields.Integer(
        string='Horas ministradas',
        compute="_compute_total_horas_aulas_ministradas"
        
    )
    
    @api.depends('aulas')
    def _compute_total_horas_aulas_ministradas(self):
        sum = 0
        for record in self:
            aulas = self.env["geracad.curso.turma.disciplina.aulas"].search(
                [('turma_disciplina_id', '=', record.id),
                ('state', '=', 'concluida')

                
                ],
                )
            for aula in aulas:
                sum = sum + aula.tempo_hora_aula_programado
        record.total_horas_aulas_ministradas = sum


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
            nota.sudo().write({
                'periodo': self.periodo
            })

        return res
    
     #usado na impressão do diário
    def get_soma_hora_aula(self):
        '''
            Função que retorna a soma de horas aula da disciplina
        '''
        aulas = self.get_aulas()
        soma = 0
        for aula in aulas:
            soma += aula.tempo_hora_aula_programado
        return soma

    #usado na impressão do diário
    def get_aulas(self):
        '''
            Função que retorna as aulas para impressão do diário final
            
        '''
        aulas = self.env['geracad.curso.turma.disciplina.aulas'].search([
            ('turma_disciplina_id','=', self.id),
            ('state','in', ['concluida']),
            
            ],order='hora_inicio_agendado ASC')
        
        return aulas
    #usado na impressão do diário
    def get_presenca_aula_matricula(self,aula, matricula_disciplina):
        '''
            Função que retorna presenca ou falta 
            
        '''
        frequencia_lines = self.env['geracad.curso.turma.disciplina.aulas.frequencia'].search([
            ('turma_aula_id','=', aula.id),
            ('matricula_disciplina_id','=', matricula_disciplina.id),
            
            ])
        for frequencia in frequencia_lines:
            return frequencia[0].count_faltas
    #usado na impressão do diário
    def get_coluna_restante_frequencia(self):
        '''
            Função que retorna quantidade de colunas na frequecia
            
        '''
        qtd_colunas_total = 40
        aulas = self.get_aulas()
        qtd_aulas = len(aulas)
        colunas_restantes = []
        for n in range(0,qtd_colunas_total-qtd_aulas):
            colunas_restantes.append(n)
        
        return colunas_restantes
    
    #usado na impressão do diário
    def get_diario_date(self):
        '''
            Função que retorna uma string da data para impressão do diário
            no formato: ex. São Luis-MA, 02 de agosto de 2022
        '''
        locale = get_lang(self.env).code
        date_diario = date.today()
        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        if self.data_encerramento:
            date_diario = self.data_encerramento

        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(date_diario,format="long",locale=locale)
        return date_str

    #usado na impressão da ata
    def get_ano_semestre(self,tipo):
        '''
            Função que retorna uma string  do ano ou do semestre da
            turma disciplina
        '''
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
            #pega todos os alunos inscritos na turma do curso
            matriculas_alunos_inscritos_no_curso = self.env['geracad.curso.matricula'].search([
                ('curso_turma_id','=',self.curso_turma_id.id),
                ('state','=','inscrito')])
                               
            matricula_disciplina_create = []
            #alunos já inscritos na disciplina
            _logger.debug("PROCURANDO MATRICULA ALUNO JA ESTÁ INSCRITO NA TURMA DISCIPLINA")
            ids_matriculas_ja_inscritos_na_disciplina = self.env['geracad.curso.matricula.disciplina'].search([
                        ('turma_disciplina_id','=',self.id)
                    ]).mapped(lambda r: r.curso_matricula_id.id) 
            
            ids_matricula_disciplina_inscrever = matriculas_alunos_inscritos_no_curso.filtered(lambda r: r.id not in ids_matriculas_ja_inscritos_na_disciplina).mapped("id")
            _logger.debug("ADICIONADA A TURMA NO FORMULARIO")
            _logger.debug(ids_matricula_disciplina_inscrever)
            matricula_disciplina_create = list(map(lambda r: {
                            'curso_matricula_id': r,
                            'turma_disciplina_id': self.id,
                            'state': 'inscrito'
                        }, ids_matricula_disciplina_inscrever))

            self.env['geracad.curso.matricula.disciplina'].create(matricula_disciplina_create)
            
    
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
    
    def action_encerrando_turmas_sistema_antigo(self, data_ini, data_fim):    
        '''
            Encerra turma disciplina via açao agendada
            
        '''
        
        res = self.env["geracad.curso.turma.disciplina"].search([
            '&',
            '&',
            ('data_abertura','<=',data_fim),
            ('data_abertura','>=',data_ini),
            ('state','not in',['cancelada','suspensa','encerrada']),
            ])
        for rec in res:
            #verificando data de encerramento
            _logger.info(rec.name)
            if not rec.data_encerramento:
                data_encerramento = rec.data_previsao_termino
            else:
                data_encerramento = rec.data_encerramento

            #verificando carga horaria
            if rec.carga_horaria == 0:
                carga_horaria = rec.disciplina_id.carga_horaria
            else:
                carga_horaria = rec.carga_horaria

            rec.write({
                'data_encerramento': data_encerramento,
                'state': 'encerrada',
                'matricula_aberta': False,
                'carga_horaria' : carga_horaria,
            })
            rec._finaliza_matricula_turma_disciplina()
                

        

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
            
            _logger.info("CARGA HORARIA")
            _logger.info(rec.disciplina_id.carga_horaria)
            _logger.info("PERIODO")
            _logger.info(periodo)
            
            result = rec.write({
                'carga_horaria': rec.disciplina_id.carga_horaria,
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
    
    def action_matricular_aluno(self):
        

        _logger.info("action matricular aluno disciplina")

        return {
            'name': _('Alunos Matriculados'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('turma_disciplina_id', '=', self.id)],
            'context': {
                'default_turma_disciplina_id': self.id,
               
            }
        }


    def action_suspender_turma_disciplina(self):
        self.write({
            'state': 'suspensa',
            'matricula_aberta': False,

        })

    def _calcula_notas_situation(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        nota_ids.action_atualiza_situation()
        
    def _encerra_notas_turma_disciplina(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        for nota in nota_ids:
            nota.action_lancar_nota()

    def _reabrir_notas_turma_disciplina(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        nota_ids.action_reabrir_nota()

    def _reabrir_matriculas_turma_disciplina(self):
        nota_ids = self.env['geracad.curso.nota.disciplina'].search([('turma_disciplina_id','=',self.id)])
        nota_ids.action_reabrir_nota()
        matriculas_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([('turma_disciplina_id','=',self.id)])
        matriculas_disciplina_ids.action_reabrir_matricula_disciplina()
        



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
        matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([
            ('turma_disciplina_id','=',self.id),
            ('state','not in',['cancelada','suspensa','encerrada']),
            ])
        for matricula_disciplina in matricula_disciplina_ids:
            matricula_disciplina.action_finaliza_matricula_disciplina()
    
    def _cancela_matricula_turma_disciplina(self):
        matricula_disciplina_ids = self.env['geracad.curso.matricula.disciplina'].search([('turma_disciplina_id','=',self.id)])
        matricula_disciplina_ids.action_cancela_matricula_disciplina()

    def action_atualiza_situation(self):
        self._calcula_notas_situation()

    def action_finalizar_aulas(self):
        dummy, act_id = self.env["ir.model.data"].sudo().get_object_reference(
            "geracad_curso", "action_geracad_curso_finalizar_aula"
        )
        vals = self.env["ir.actions.act_window"].sudo().browse(act_id).read()[0]
        vals["context"] = {
            "default_turma_disciplina_id": self.id,
        }
        return vals
    
    def action_reabrir_aulas(self):

        self.write({
            'state': 'aberta',
            'matricula_aberta': True,
            'data_termino': None,
            'data_encerramento': None,
            })
        self._reabrir_notas_turma_disciplina()
        self._reabrir_matriculas_turma_disciplina()

    def action_reabrir_turma(self):

        self.write({
            'state': 'aberta',
            'matricula_aberta': True,
            'data_termino': None,
            'data_encerramento': None,
            })
        
        self._reabrir_notas_turma_disciplina()

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

        

    
       
