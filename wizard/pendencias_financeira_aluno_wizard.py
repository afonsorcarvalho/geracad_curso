# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, date
from babel.dates import format_datetime, format_date
from odoo.tools.misc import formatLang, format_date as odoo_format_date, get_lang

from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class GeracadCursoPendenciasFinanceirasAlunoWizard(models.TransientModel):
    _name = "geracad.curso.pendencias.financeira.aluno.wizard"
    _description = "Assistente de imprimir pendencias financeiras de alunos"

    aluno_id = fields.Many2one('res.partner',
        domain=[('e_aluno','=',True)]
    )
    matricula_id = fields.Many2one('geracad.curso.matricula',
        
        
    )
    domain_matricula_id = fields.Char(
        compute="_compute_domain_matricula_id",
        readonly=True,
        store=False,
    )

    @api.depends('aluno_id')
    def _compute_domain_matricula_id(self):
        for rec in self:
            domain_matricula_id = []
            if rec.aluno_id:
                domain_matricula_id = [('aluno_id', '=', rec.aluno_id.id)] 
            rec.domain_matricula_id = json.dumps(domain_matricula_id)
    
    
   
    def get_parcelas(self, status = 'todas', count = False, sum = False):

       
        
        domain_filter = []
        if status == 'todas':
            domain_filter = []
          
        if status == 'pagas':
            domain_filter.append(('esta_pago', '=', True ))
    
        if status == 'abertas':
            domain_filter.append(('esta_pago', '=', False ))
          
        if status == 'vencidas':
            domain_filter.append(('esta_pago', '=', False )) 
            domain_filter.append(('data_vencimento','<', datetime.today())) 
               
        if status == 'a_vencer':
            domain_filter.append(('esta_pago', '=', False )) 
            domain_filter.append(('data_vencimento','>=', datetime.today())) 
 
        if self.matricula_id:
            domain_filter.append(('curso_matricula_id','=',self.matricula_id.id))

        if self.aluno_id:
            domain_filter.append(('aluno_id','=',self.aluno_id.id))
        
        parcelas = self.env['geracad.curso.financeiro.parcelas'].search(domain_filter, 
                offset=0, limit=100, order="data_vencimento ASC ", count=count
            )
        soma = 0
        for parc in parcelas:
            soma +=parc.valor
        if sum: 
            return soma
        if not sum: 
            return parcelas
    
    def get_date_str(self):
        '''
        Função retorna a data no formato ex. 'São Luís-MA, 20 de Abril de 2022'
        '''
        date_hoje = date.today()
        locale = get_lang(self.env).code

       
        date_str = self.env.user.company_id.city_id.name + '-' + self.env.user.company_id.state_id.code + ', ' + format_date(date_hoje,format="long",locale=locale)
        return   date_str

    def action_confirm(self):
        """
        
        """
        _logger.debug("confirmado")
        if not self.matricula_id and not self.aluno_id:
            raise ValidationError('Nenhum aluno ou matricula foi selecionada')
        return self.env.ref("geracad_curso.action_pendencias_financeira_aluno_report").report_action(self)
       
