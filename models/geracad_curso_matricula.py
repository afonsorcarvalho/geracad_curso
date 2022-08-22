# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _
from datetime import date, timedelta

from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, misc

import logging

_logger = logging.getLogger(__name__)

class GeracadCursoMatricula(models.Model):
    _name = "geracad.curso.matricula"
    _description = "matricula de Cursos"
    _check_company_auto = True


    
    _inherit = ['portal.mixin','mail.thread']
    


    name = fields.Char("Código", tracking=True)

    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True,
         default=lambda self: self.env.company,
         tracking=True
        
    )
    edit_turma_curso =  fields.Boolean(tracking=True)

    curso_turma_id = fields.Many2one(
        'geracad.curso.turma',
        string='Turma',
        required=True,
        tracking=True
        )

    @api.onchange('curso_turma_id')
    def onchange_curso_turma_id(self):
        self.curso_grade_version = self.curso_turma_id.curso_grade_version
    
    curso_grade_version = fields.Many2one(
        string='Versão Grade',
        comodel_name='geracad.curso.grade.versao',
        
    )
    curso_grade_version_domain = fields.Char(
        compute="_compute_curso_grade_version_domain"
    )

    
    @api.depends('curso_id')
    def _compute_curso_grade_version_domain(self):
        for rec in self:
            _logger.info("curso id")
            rec.curso_grade_version_domain = ""
            if rec.curso_id:
                rec.curso_grade_version_domain = json.dumps([('curso_id','=',rec.curso_id.id)])
    
    
    
    
    curso_nome = fields.Char( 
        related='curso_turma_id.curso_id.name',
        string="Nome do curso",
        readonly=True,
        store=True
    )
    curso_id = fields.Many2one( 
        related='curso_turma_id.curso_id',
        string="Curso",
        readonly=True,
        store=True
    )

    @api.onchange('curso_id')
    def onchange_curso_id(self):
        
         ''' Ao mudar o curso procura a versão mais nova da grade do curso'''
         _logger.info("curso_id mudou")
         for record in self:

             _logger.info(record.curso_id.id)
             if record.curso_id:
    
                grade_version = self.env['geracad.curso.grade.versao'].search([('curso_id','=',record.curso_id.id)],
                     limit=1,
                    
                     )
                _logger.info("achei a grade")
                _logger.info(grade_version)
                if len(grade_version) > 0:
                    record.curso_grade_version = grade_version[0].id
                    
    curso_type = fields.Many2one(
        string='Tipo do Curso',
        comodel_name="geracad.curso.type",related='curso_id.type_curso',
        store=True,
        readonly=True
        
    )
   
    curso_turma_codigo = fields.Char( 
        related='curso_turma_id.name',
        string="Código da turma",
        readonly=True,
        store=True
    )
    aluno_id = fields.Many2one(
        'res.partner',
        string='Aluno',
        required=True,
        
        domain=[('e_aluno','=',True)]
        
        )  
    nome_pai = fields.Char( 
        related='aluno_id.nome_pai',
        string="Nome do Pai",
        readonly=True,
        store=True
    )
    nome_mae = fields.Char( 
        related='aluno_id.nome_mae',
        string="Nome do mãe",
        readonly=True,
        store=True
    )
   
    data_nascimento = fields.Date( 
        related='aluno_id.data_nascimento',
        string="Data Nascimento",
        readonly=True,
        store=True
    )
    state_id = fields.Char( 
        related='aluno_id.state_id.name',
        string="UF",
        readonly=True,
        store=True
    )
    city = fields.Char( 
        related='aluno_id.city',
        string="cidade",
        readonly=True,
        store=True
    )
    aluno_mobile =  fields.Char(related='aluno_id.mobile',readonly=True) 
   
    data_matricula = fields.Date(
        string='Data Matrícula',
        default=fields.Date.context_today,
        tracking=True
    )

    data_previsao_conclusao = fields.Date(
        string='Data Prevista Conclusão',
        default= lambda self: date.today() +  relativedelta(months=24),
        tracking=True
    )
   
    data_conclusao = fields.Date(
        string='Data Conclusão',
        
        tracking=True
    )
   
    state = fields.Selection([
        ('draft', 'Rascunho'),
        ('inscrito', 'Inscrito'),
        ('trancado', 'Trancada'),
        ('abandono', 'Abandono'), 
        ('cancelada', 'Cancelada'),
        ('expulso', 'Expulso'), 
        ('falecido', 'Falecido'),
        ('formado', 'Formado'),
        ('transferido', 'Transferido'),
        
    ], string="Status", default="draft", readonly=False, tracking=True 
    )

    matriculas_disciplina_ids = fields.One2many(
        "geracad.curso.matricula.disciplina", inverse_name = 'curso_matricula_id',
        readonly=True)

    matriculas_disciplinas_count = fields.Integer(
        string='Disciplinas', 
        compute='_compute_matriculas_disciplinas',
        )

    notas_disciplinas_count = fields.Integer(
        string='Disciplinas', 
        compute='_compute_notas_disciplinas',
        )

    contratos_count = fields.Integer(
        string='Contratos', 
        compute='_compute_contratos',    
        )

    parcelas_ids = fields.One2many('geracad.curso.financeiro.parcelas', 'curso_matricula_id')

    parcelas_count = fields.Integer(
        string='Qtd. Parcelas', 
        compute='_compute_parcelas',
        )
    
    contrato_gerado = fields.Boolean("Gerado Contrato?",tracking=True ,readonly=True)

    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if 'company_id' in vals:
             curso_turma = self.env['geracad.curso.turma'].search([('id', '=', vals['curso_turma_id'] )])
             self = self.with_company(curso_turma.company_id)

        if vals.get('name', _('New')) == _('New'):
             seq_date = None
        vals['name'] = self._gera_codigo_matricula(vals) or _('New')
        vals['state'] = 'inscrito'
        
        result = super(GeracadCursoMatricula, self).create(vals)
        return result
    
    #TODO
    # verificar  essa função está certa e funcionando
    def write(self, vals):
        res = super(GeracadCursoMatricula, self).write(vals)

        if self.edit_turma_curso:
            vals['edit_turma_curso'] = False
        
        return res
    
    @api.depends('name', 'curso_turma_id')
    def name_get(self):
        result = []
        for record in self:
            name = '[' + record.name + '] ' + record.aluno_id.name
            result.append((record.id, name))
        return result
    
    # COMPUTE FUNCTIONS
    #
    def _compute_matriculas_disciplinas(self):
        for record in self:    
            record.matriculas_disciplinas_count = self.env["geracad.curso.matricula.disciplina"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
                
    def _compute_notas_disciplinas(self):
        for record in self:    
            record.notas_disciplinas_count = self.env["geracad.curso.nota.disciplina"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
   
    def _compute_contratos(self):
        for record in self:    
            record.contratos_count = self.env["geracad.curso.contrato"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)

    def _compute_parcelas(self):
        for record in self:    
            record.parcelas_count = self.env["geracad.curso.financeiro.parcelas"].search(
                [('curso_matricula_id', '=', record.id)],
                offset=0, limit=None, order=None, count=True)
    

    # ONCHANGE FUNCTIONS
    #

    @api.onchange('curso_turma_id')
    def _onchange_curso_turma_id(self):
        _logger.debug("MUDANCA NA TURMA DE CURSO")
        
        if self.curso_turma_id.id:
            vals={
                'curso_turma_id': self.curso_turma_id.id
            }
        
            self.name = self._gera_codigo_matricula(vals)
        
    # PRIVATE FUNCTIONS
    #
    def _gera_codigo_matricula(self,vals):
        """
            Gera o codigo da matricula de cursos pegando o codigo da turma de curso + número sequencial
        """

        curso_turma = self.env['geracad.curso.turma'].search([('id', '=', vals['curso_turma_id'] )])
        _logger.info(curso_turma.name)
        
        
        codigo_matricula = curso_turma.name + "-"
        codigo_matricula += self._get_number_sequencial(curso_turma.name)
        _logger.info(codigo_matricula)
        return codigo_matricula

 

    def _get_number_sequencial(self, codigo_turma):

        _logger.info('PROCURANDO MATRICULAS NA TURMA:')
        _logger.info(codigo_turma)
        matriculas = self.env['geracad.curso.matricula'].search([('name', '=like', codigo_turma+"%")], order="name asc")
        
        if len(matriculas) == 0:
            _logger.info('NENHUMA MATRICULA ENCONTRADA')
            return "01"
        _logger.info('MATRICULAS ENCONTRADAS')
        for matricula in matriculas:
            
            _logger.info(matricula.name)
            _logger.info(matricula.name[-2:])
            number_sequencial_string = matricula.name[-2:]
            number_sequencial = int(number_sequencial_string)+1
        resultado_string ="{:02d}"
        return resultado_string.format(number_sequencial)

    
    def _get_periodos(self):
        '''
        Retorna a quantidade de periodo do curso
        '''
        res = []
        for periodo in range(self.curso_id.quantidade_de_periodos):
                res.append(periodo+1)   
        return res  

    def _pega_periodo_disciplina_sem_periodo(self,disciplina_id):
        '''
            recebe uma discplina e retorna o periodo dela
        '''
        periodo = 0
        versao_grade = self.curso_grade_version
        grade_line_ids = self.env['geracad.curso.grade'].search([
            ('disciplina_id','=',disciplina_id.id),
            ('version_grade_id','=', versao_grade.id)

            ])
        for grade_line in grade_line_ids:
            if grade_line.periodo == 0:
                
                periodo = 1
            else:
                periodo = grade_line.periodo
        return periodo


    def _get_notas_periodo(self, periodo):
        '''
        Retorna as notas de um periodo para impressao do historico
        '''
        if self.state != 'formado':    
            nota_disciplina_ids = self.env['geracad.curso.nota.disciplina'].search([
                '&',
                ('curso_matricula_id', '=', self.id),
                '&',
                ('state','not in', ['cancelada']),
                '&',
                ('periodo','=', int(periodo)),
                ('disciplina_id.e_estagio','=', False)
                ])
        else:
            nota_disciplina_ids = self.env['geracad.curso.nota.disciplina.historico.final'].search([
                ('curso_matricula_id', '=', self.id),
                '&',
                ('disciplina_id.e_estagio','=', False),
                ('periodo','=', int(periodo))
                ])

        nota_disciplina_ids_periodo = []
        for nota_disciplina_id in nota_disciplina_ids:
            _logger.info(nota_disciplina_id.disciplina_id.name)
            _logger.info("PERIODO")
            _logger.info(nota_disciplina_id.periodo)
            if nota_disciplina_id.periodo == 0:
                if nota_disciplina_id.turma_disciplina_id.periodo == 0:
                    periodo_nota = self._pega_periodo_disciplina_sem_periodo(nota_disciplina_id.disciplina_id)
                else:
                    periodo_nota = nota_disciplina_id.turma_disciplina_id.periodo
            else:
                periodo_nota = nota_disciplina_id.periodo
            if periodo_nota == int(periodo):
                nota_disciplina_ids_periodo.append(nota_disciplina_id)
    

        
        return nota_disciplina_ids_periodo

    def _tem_notas_periodo(self,periodo):
        count_disciplinas = len(self._get_notas_periodo(periodo))
        return count_disciplinas
    
    def _get_disciplinas_pendentes(self):
        '''
        Função usada na impressão de disciplinas pendentes do aluno
        retorna uma lista de disciplinas pendentes com 
        Código, Nome e Carga horária.
        '''
        _logger.info("Pegando disciplinas pendentes")
        analise_disciplinas_ids= self._get_disciplinas_analise_ids()
        _logger.info(analise_disciplinas_ids)
        disciplinas_pendentes = analise_disciplinas_ids['disciplinas_faltantes']
        return self.env['geracad.curso.disciplina'].search([('id','in',disciplinas_pendentes)])

    def _calc_carga_horaria_pendente_cursada(self):
        _logger.info("Calculando carga horaria pendente")
        analise_disciplinas_ids= self._get_disciplinas_analise_ids()
        disciplinas_pendentes_ids = analise_disciplinas_ids['disciplinas_faltantes']
        disciplinas_cursadas_ids = analise_disciplinas_ids['disciplinas_cursadas']
        disciplinas_pendentes = self.env['geracad.curso.disciplina'].search([('id','in',disciplinas_pendentes_ids)])
        disciplinas_cursadas =  self.env['geracad.curso.disciplina'].search([('id','in',disciplinas_cursadas_ids)])
        disciplinas_pendentes_ch_total = 0
        disciplinas_cursada_ch_total = 0
        for disciplina_pen in disciplinas_pendentes:
            disciplinas_pendentes_ch_total = disciplinas_pendentes_ch_total + disciplina_pen.carga_horaria
        for disciplina_cur in disciplinas_cursadas:
            disciplinas_cursada_ch_total = disciplinas_cursada_ch_total + disciplina_cur.carga_horaria
        return {
            'disciplinas_cursada_ch_total' : disciplinas_cursada_ch_total,
            'disciplinas_pendentes_ch_total' : disciplinas_pendentes_ch_total,

        }





    def _get_nota_estagio(self, count = False):
        if self.state != 'formado':
            return self.env['geracad.curso.nota.disciplina'].search([
                '&',
                ('curso_matricula_id', '=', self.id),
                '&',
                ('state','not in', ['cancelada']),
                ('disciplina_id.e_estagio','=', True)
                ], count = count)
        return self.env['geracad.curso.nota.disciplina.historico.final'].search([
                ('curso_matricula_id', '=', self.id),
                ('disciplina_id.e_estagio','=', True)
                ], count = count)

    def _tem_estagio(self):
        return self._get_nota_estagio(True)
        

    # def _get_portal_return_action(self):
    #     """ Return the action used to display matriculas when returning from customer portal. """
    #     self.ensure_one()
    #     return self.env.ref('sale.action_quotations_with_onboarding')
    
    # url de acesso no portal
    def _compute_access_url(self):
        super(GeracadCursoMatricula, self)._compute_access_url()
        for matricula in self:
            matricula.access_url = '/my/matriculas/%s' % matricula.id

    # url de nome do aquivo download no portal
    def _get_report_base_filename(self):
        self.ensure_one()
        return 'Histórico - %s' % (self.name)
    
    
    #TODO.
    # 
    #  FAZER ACTION FALECIMENTO
    #  
    
    def _muda_situacao_nota_e_matricula_disciplina(nota_id,situacao):
        _logger.debug("mudando situação da nota")
    
    def _tem_contrato_vigente(self):
        contratos_vigentes_count = self.env["geracad.curso.contrato"].search([ 
        '&',
        ('curso_matricula_id','=', self.id),
        '|',
        ('state','=', 'vigente'),
        ('state','=', 'draft'),
            ], offset=0, limit=None, order=None, count=True)
        if contratos_vigentes_count > 0:
            return True
        else:
            return False

    def _suspende_contrato(self):
        self._muda_state_contrato('suspenso')

    def _cancela_contrato(self):
        self._muda_state_contrato('cancelado')


    def _muda_state_contrato(self,state):
        
        contrato_ids = self.env["geracad.curso.contrato"].search([
        
        ('curso_matricula_id','=', self.id)
            ], offset=0, limit=None, order=None, count=False)
        for contrato in contrato_ids:
            if contrato.state == 'vigente' or contrato.state == 'draft':
                contrato.write({
                    'state': state
                })


    ##########################################
    #  FUNCOES USADAS NA IMPRESSAO
    ##########################################
        
    
   
    def get_periodo_cursado(self):
        '''
        Função utilizada para verficar o período cursado atual do aluno, utilizada na impressão
        da declaração
        '''
        matricula_disciplina_ids = self.env["geracad.curso.matricula.disciplina"].search([
            '&',
            ('curso_matricula_id','=', self.id),
            ('state','not in', ['cancelada','trancado','expulso']),
            ],order='data_matricula DESC',limit=1)

        if len(matricula_disciplina_ids):
            periodo = matricula_disciplina_ids[0].turma_disciplina_id.periodo
        else:
            periodo = 1
        return periodo
        

    def get_date_str(self):
        '''
        Função retorna a data no formato ex. 'São Luís-MA, 20 de Abril de 2022'
        '''
        date_hoje = date.today()
        locale = get_lang(self.env).code

        _logger.info(self.company_id.city_id.name + '-' + self.company_id.state_id.code)
        date_str = self.company_id.city_id.name + '-' + self.company_id.state_id.code + ', ' + format_date(date_hoje,format="long",locale=locale)
        return   date_str

   
    #########################################
    # MUDA TODAS AS PARCELAS COM DATA DE VENCIMENTO DEPOIS DO DIA ATUAL
    
    def _cancela_parcelas_a_vencer(self):
        _logger.debug("cancelando parcelas")
        self._muda_state_parcelas_a_vencer('cancelado', True)


    def _suspende_parcelas_a_vencer(self):
        _logger.debug("suspendendo parcelas")
        self._muda_state_parcelas_a_vencer('suspenso', True)

    def _muda_state_parcelas_a_vencer(self,state, active):
        _logger.debug("mudando situação das parcelas a vencer")
        date_atual = (date.today() - timedelta(days=1)).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        parcelas_ids = self.env["geracad.curso.financeiro.parcelas"].search([
            '&',('data_vencimento', '>', date_atual),
            ('curso_matricula_id','=', self.id)
            
            
            ], offset=0, limit=None, order=None, count=False)
        _logger.debug(parcelas_ids)
        for parcela in parcelas_ids:
            _logger.debug(parcela)
            if not parcela.esta_pago:
                _logger.debug(state)
                parcela.write({
                    'state': state,
                    'active': active,

                })
    def _muda_state_parcelas(self,state,active):
        _logger.debug("mudando situação das parcelas")
        
        
        parcelas_ids = self.env["geracad.curso.financeiro.parcelas"].search([
            '&',
            ('curso_matricula_id','=', self.id),
           
            '|',
            ('active','=', False),
            ('active','=', True),

            
            
            ], offset=0, limit=None, order=None, count=False)
        _logger.debug(parcelas_ids)
        for parcela in parcelas_ids:
            _logger.debug(parcela)
            if not parcela.esta_pago:
                _logger.debug(state)
                parcela.write({
                    'state': state,
                    'active': active,

                })
    """

            BUTTON ACTIONS

    """
    def action_calcula_medias_novamente(self):
        _logger.info("Calcula media novamente")
        records_ids = self.env["geracad.curso.nota.disciplina"].search([('situation', '=', 'AP')], offset=0, limit=None, order=None, count=False)
        records_ids._compute_media()

    def action_ajeita_versao_grade_matricula_curso(self):
        _logger.info("Mudando versao da grade na matricula")
        res = self.env["geracad.curso.matricula"].search([])
        for rec in res:
            rec.onchange_curso_turma_id()
        
        

    def action_muda_unidade_matricula(self):
        _logger.info("Muda unidade da matricula")
        #procurando parauapebas
        records_ids = self.search([('name', 'ilike', 'CJ%')], offset=0, limit=None, order=None, count=False)
        for record in records_ids:
            _logger.info(record.name)
            record.write({
                'company_id': 3
            }) 
        #procurando belem
        records_ids = self.search([('name', 'ilike', 'BL%')], offset=0, limit=None, order=None, count=False)
        for record in records_ids:
            _logger.info(record.name)
            record.write({
                'company_id': 2
            }) 
           

    def action_gerar_contrato(self):
        _logger.info("Gerando Contrato")
        return {
            'name': _('Gerar Contrato'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'form',
            'res_model': 'geracad.curso.contrato',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }


    def action_trancar(self):
        _logger.info("Matrícula Trancada")
        for matricula_disciplina in self.matriculas_disciplina_ids:
            _logger.info(matricula_disciplina.name)

            nota_ids = self.env["geracad.curso.nota.disciplina"].search([('disciplina_matricula_id','=',matricula_disciplina.id)])
            for nota in nota_ids:
                if nota.situation == 'IN':
                    _logger.info("trancada")
                    nota.write({
                        'situation': 'TR',
                        
                    })
            matricula_disciplina.write({
                'state': 'trancado'

            })
        self.write({'state': 'trancado'})
        self._suspende_parcelas_a_vencer()
        self._suspende_contrato()

    def action_reativar(self):
        _logger.info("Matrícula Reativada")

        self.write({'state': 'inscrito'})
        self._muda_state_parcelas('vigente',True)
        for matricula_disciplina in self.matriculas_disciplina_ids:
            matricula_disciplina.write({
                'state': 'inscrito'

            })

    
   
    
    def action_abandono(self):
        _logger.info("Matrícula Abandonada")
        for matricula_disciplina in self.matriculas_disciplina_ids:
            _logger.info(matricula_disciplina.name)
            nota_aluno_ids = self.env['geracad.curso.nota.disciplina'].search([
                ('disciplina_matricula_id','=',matricula_disciplina.id)])

            for nota in nota_aluno_ids:
                if nota.situation == 'IN':
                    _logger.info("abandonada")
                    nota.write({
                        'situation': 'AB',
                        'state': 'concluida',
                    })
            matricula_disciplina.write({
                'state': 'abandono'

            })

        self.write({'state': 'abandono'})
        self._cancela_parcelas_a_vencer()
        self._cancela_contrato()


    
    

    def action_habilita_edit_turma_curso(self):
        _logger.info("Edita Turma Curso")
        self.write({
            'edit_turma_curso': True,
        })
    def action_desabilita_edit_turma_curso(self):
        _logger.info("Desbilita Turma Curso")
        self.write({
            'edit_turma_curso': False,
        })
    
    def _get_disciplinas_cursadas_ids(self):
        '''
            Retorna um List das disciplinas cursadas apenas com os ids
        '''
        disciplinas_ids = []
        res = self.env["geracad.curso.nota.disciplina"].search([
            '&',
            ('curso_matricula_id', '=',self.id ),
            ('situation', 'in',['AP','AM','EA'] )
            ], offset=0, limit=None, order=None, count=False)

        for nota in res:
            disciplinas_ids.append(nota.disciplina_id.id)
        return disciplinas_ids

    def _get_disciplinas_curso_obrigatorias_ids(self):
        '''
            Retorna uma lista apenas com os ids das disciplinas 
            obrigatorias
        '''
        disciplinas_ids = []
        res = self.env["geracad.curso.grade"].search([
            '&',
           # ('curso_id', '=',self.curso_id.id),   
           # '&', 
            ('version_grade_id', '=',self.curso_grade_version.id),    
            ('e_obrigatoria', '=',1 )
            ], offset=0, limit=None, order=None, count=False)
        _logger.info("PROCURANDO DISCIPLINAS OBRIGATÓRIAS")
        _logger.info(res)
        for grade in res:
            disciplinas_ids.append(grade.disciplina_id.id)
            
        return disciplinas_ids
    
    def _get_disciplinas_com_equivalentes_ids(self, disciplinas_ids_list):
        '''
            Recebe uma lista de ids de disciplinas e retorna
            a lista recebida mais todas as suas disciplinas equivalentes
        '''
        disciplinas_equivalentes_ids = [] 
       

        for disciplina_id in disciplinas_ids_list:
            disciplina_line_ids  = self.env['geracad.curso.equivalencia.disciplina.line'].search([
                ('disciplinas_equivalente_id','=', disciplina_id)
                ])
            _logger.info('DISCIPLINAS equivalentes line ')
            _logger.info(disciplina_line_ids)
            for disciplina_equivalentes_line in disciplina_line_ids:
                disciplinas_equivalentes_ids.append(disciplina_equivalentes_line.disciplinas_id.id)
        return disciplinas_ids_list + disciplinas_equivalentes_ids

    def _get_disciplinas_analise_ids(self):
        '''
            Analisa as disciplinas cursadas com as obrigatorias
            Retorna um map com 'disciplinas_faltantes' e 'disciplinas_cursadas'
        '''
        disciplina_concluida_ids = self._get_disciplinas_cursadas_ids()
        _logger.info('DISCIPLINAS CURSADAS ')
        _logger.info(disciplina_concluida_ids)
        disciplinas_cursadas_com_equivalentes = self._get_disciplinas_com_equivalentes_ids(disciplina_concluida_ids)
        _logger.info('DISCIPLINAS CURSADAS COM SUAS EQUIVALENTES')
        _logger.info(disciplinas_cursadas_com_equivalentes)
        disciplinas_obrigatorias_id = self._get_disciplinas_curso_obrigatorias_ids()
        _logger.info(disciplinas_obrigatorias_id)
        disciplinas_faltantes = []
        disciplinas_cursadas = []
        for disciplina_obrigatoria in disciplinas_obrigatorias_id:
 
            if disciplina_obrigatoria in disciplinas_cursadas_com_equivalentes:
                disciplinas_cursadas.append(disciplina_obrigatoria)
            else:
                disciplinas_faltantes.append(disciplina_obrigatoria)
            
        _logger.info("disciplinas_cursadas")
        _logger.info(disciplinas_cursadas)

        _logger.info("disciplinas_faltantes")
        _logger.info(disciplinas_faltantes)
        return {'disciplinas_faltantes':disciplinas_faltantes,'disciplinas_cursadas':disciplinas_cursadas}

  
    def _atualiza_periodo_de_nota_com_turma_disciplina(self):
        '''
            Função que atualiza as notas do aluno com os respectivos periodos de acordo 
            com a turma disciplina 
        '''
        for rec in self:
            notas = self.env["geracad.curso.nota.disciplina"].search([('curso_matricula_id','=',rec.id)])
            for nota in notas:
                nota.periodo = nota.turma_disciplina_id.periodo

    def _atualiza_periodo_turma_disciplina_com_grade(self):
        '''
            Função que atualiza as turmas de disciplinas com os respectivos periodos de acordo 
            com a grade curricular da matricula do curso do aluno 
        '''
        for rec in self:
            matricula_disciplina_line = self.env["geracad.curso.matricula.disciplina"].search([
               
                ('curso_matricula_id','=',rec.id),
                       
                ])
            _logger.info(matricula_disciplina_line)
            for matricula_disciplina in matricula_disciplina_line:   
                _logger.info(matricula_disciplina.disciplina_id.name)
                _logger.info(rec.curso_grade_version.name)

                grade_line = self.env["geracad.curso.grade"].search([
                    '&',
                    ('version_grade_id','=',rec.curso_grade_version.id),
                    ('disciplina_id','=',matricula_disciplina.disciplina_id.id)
                    
                    ])
                _logger.info(grade_line)
                for grade in grade_line:    
                    turma_disciplina = self.env["geracad.curso.turma.disciplina"].search([
                        ('id','=',matricula_disciplina.turma_disciplina_id.id)])
                    _logger.info(turma_disciplina)
                    _logger.info(grade.periodo)
                    turma_disciplina.write({
                        'periodo' : grade.periodo
                        })

    def action_atualizar_historico(self):
        if not self.curso_grade_version:
            raise ValidationError('Por favor, insiria a Versão da Grade na matrícula')
        for rec in self:
            rec._atualiza_periodo_turma_disciplina_com_grade()
            rec._atualiza_periodo_de_nota_com_turma_disciplina()
        
        return self.env.ref("geracad_curso.action_historico_aluno_report").report_action(self)


    def action_disciplinas_pendentes(self):
        '''
            Action que gera report de disciplinas pendentes
        '''
        _logger.info("Action Disciplinas Pendentes")
        if not self.curso_grade_version:
            raise ValidationError('Por favor, insiria a Versão da Grade na matrícula')
        return self.env.ref("geracad_curso.action_historico_disciplinas_pendentes_aluno_report").report_action(self)
        # analise_disciplinas_ids= self._get_disciplinas_analise_ids()
        
        # disciplinas_pendentes = analise_disciplinas_ids['disciplinas_faltantes']
        # return self.env['geracad.curso.disciplnas'].search([('id','in',disciplinas_pendentes)])

    def action_gera_historico_final(self):
        '''
            Action que gera a wizard de geração do histórico final da matrícula
            Mostrando as disciplinas faltantes e concluídas
        '''

        
        _logger.info("Gerando Histórico final")
        if not self.curso_grade_version:
            raise ValidationError('Por favor, insiria a Versão da Grade na matrícula')
        
        _logger.info("PROCURANDO TURMAS DISCIPLINAS SEM PERIODO")
        
        dummy, act_id = self.env["ir.model.data"].sudo().get_object_reference(
            "geracad_curso", "action_geracad_curso_gerar_historico_final"
        )
        disciplinas_faltantes_ids= self._get_disciplinas_analise_ids()
        disciplinas_faltantes_values = []
        disciplinas_cursadas_values = []
        for disciplina in disciplinas_faltantes_ids['disciplinas_faltantes']:
            disciplinas_faltantes_values.append((0,0, {'disciplina_id': disciplina, 'concluida':0}))
        for disciplina in disciplinas_faltantes_ids['disciplinas_cursadas']:
            disciplinas_cursadas_values.append((0,0, {'disciplina_id': disciplina, 'concluida':1}))
        _logger.debug(disciplinas_faltantes_values)
        _logger.debug(disciplinas_cursadas_values)
        _logger.debug("chamando a wizard")
        vals = self.env["ir.actions.act_window"].sudo().browse(act_id).read()[0]
        vals["context"] = {
            "default_matricula_id": self.id,
            "default_disciplina_faltantes_id": disciplinas_faltantes_values,
            "default_disciplina_concluidas_id": disciplinas_cursadas_values
          
        }
        return vals

    def action_go_matriculas_disciplinas(self):

        _logger.info("action open matriculas disciplinas")
        
        return {
            'name': _('Matrículas em Disciplinas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.matricula.disciplina',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
                'group_by': ['state'],
                'expand': True
            }
        }
        
    def action_go_notas_disciplinas(self):

        _logger.info("action open notas disciplinas")
        
        return {
            'name': _('Notas Disciplinas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.nota.disciplina',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
     
            }
        }
    
    
    def action_go_gera_contrato(self):

        _logger.info("action open gera contrato")
        self._tem_contrato_vigente()
        
        return {
            'name': _('Gerar Contrato'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'form',
            'res_model': 'geracad.curso.contrato',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }
    def action_go_contratos(self):

        _logger.info("action open contratos")
        self._tem_contrato_vigente()
        
        return {
            'name': _('Contratos do Aluno'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.contrato',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }
    def action_go_parcelas(self):

        _logger.info("action open financeiro parcelas")
        
        return {
            'name': _('Financeiro Parcelas'),
            'type': 'ir.actions.act_window',
            'target':'current',
            'view_mode': 'tree,form',
            'res_model': 'geracad.curso.financeiro.parcelas',
            'domain': [('curso_matricula_id', '=', self.id)],
            'context': {
                'default_curso_matricula_id': self.id,
             
            }
        }
        

   

        

    
       