# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class GeracadCursoPagamentoParcela(models.TransientModel):
    _name = "geracad.curso.pagamento.parcela"
    _description = "Assistente de Pagamentos de parcela"

    company_id = fields.Many2one(
        'res.company', string="Unidade", required=True, readonly=True,default=lambda self: self.env.company
    )

    parcela_id = fields.Many2one(
        "geracad.curso.financeiro.parcelas", readonly=True, string="Parcela"
    )
    
   
    aluno_id = fields.Many2one(
        "res.partner", string="Aluno", readonly=True
    )
    
    communication = fields.Char(string="Anotações")
    data_pagamento = fields.Date(
        string="Data do Pagamento",
        default=fields.Date.context_today,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Moeda",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )
   
    valor_devido = fields.Monetary(string="Valor a receber", required=True, )
    valor_pago = fields.Monetary(string="Valor do Pagamento", required=True, )
    
    forma_de_pagamento = fields.Selection(
        string = 'Forma de Pagamento',
        selection = [('dinheiro', 'Dinheiro'), 
            ('boleto', 'Boleto'),
            ('cheque', 'Cheque'),
            ('emp_cobranca', 'Empresa de Cobrança'), 
            ('debito', 'Cartão Débito'), 
            ('credito', 'Cartão Crédito'), 
            ('deposito', 'Depósito Bancário'),
            ('tribunal','Tribunal'), 
            
            ],
        required=True,
      

    )

    @api.model
    def default_get(self, fields):
        rec = super(GeracadCursoPagamentoParcela, self).default_get(fields)
        

        return rec

    def _get_payment_vals(self):
        """
        Method responsible for generating payment record amounts
        """
        
        vals = {
            "aluno_id": self.aluno_id.id,
            "parcela_id": self.parcela_id.id,
            "data_pagamento": self.data_pagamento,
            "valor_devido": self.valor_devido,
            "valor_pago": self.valor_pago,
            "currency_id": self.currency_id.id,
            "forma_de_pagamento": self.forma_de_pagamento.id,
        }
        return vals

    def action_confirm_payment(self):
        """
        Method responsible for creating the payment
        """
        _logger.debug("confirmado pagamento")
        self.parcela_id.write({
            'valor_pago': self.valor_pago,
            'esta_pago': True,
            'data_pagamento': self.data_pagamento,
            'observacao': self.communication,
            'forma_de_pagamento': self.forma_de_pagamento,
            'state': 'recebido',
        })
