# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import binascii


from odoo import fields, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.mail import _message_post_helper
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.osv import expression


class MatriculasPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        matriculas = request.env['geracad.curso.matricula']
        parcelas = request.env['geracad.curso.financeiro.parcelas']
        if 'matriculas_count' in counters:
            values['matriculas_count'] = matriculas.search_count([('aluno_id', '=', partner.id)]) 
        if 'parcelas_count' in counters:
            values['parcelas_count'] = parcelas.sudo().search_count([('aluno_id', '=', partner.id)]) 
            
            print('matriculas_count')
            print(values)
        return values
            
    def _prepare_portal_layout_values(self):
        """Values for /my/* templates rendering.

        Does not include the record counts.
        """
        # get customer sales rep
        sales_user = False
        partner = request.env.user.partner_id
        if partner.user_id and not partner.user_id._is_public():
            sales_user = partner.user_id

        return {
            'sales_user': sales_user,
            'page_name': 'home',
        }     
        
        
        return values

    # ------------------------------------------------------------
    # My Matriculas
    # ------------------------------------------------------------

    def _matricula_get_page_view_values(self, matricula, access_token, **kwargs):
        values = {
            'page_name': 'matricula',
            'matricula': matricula,
            'report_type': 'html',
        }
        return self._get_page_view_values(matricula, access_token, values, 'my_matriculas_history', False, **kwargs)

    def _order_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'matricula': order,
            'token': access_token,
           
            'bootstrap_formatting': True,
            'aluno_id': order.aluno_id.id,
            'report_type': 'html',
            
        }
        if order.company_id:
            values['res_company'] = order.company_id

        

        
        history = request.session.get('my_orders_history', [])
        values.update(get_records_pager(history, order))

        return values

    #
    # matriculas
    #

    @http.route(['/my/matriculas', '/my/matriculas/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_matriculas(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        GeracadCursoMatricula = request.env['geracad.curso.matricula']

        domain = [
            
            ('aluno_id', '=', partner.id)
        ]

        searchbar_sortings = {
            'date': {'label': _('Data Matricula'), 'order': 'data_matricula desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_matricula = searchbar_sortings[sortby]['order']

        # count for pager
        matricula_count = GeracadCursoMatricula.search_count(domain)
        matricula_count = 1
        print("matricula_count")
        print(matricula_count)
        
        # make pager
        pager = portal_pager(
            url="/my/matriculas",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=matricula_count,
            page=page,
            step=self._items_per_page
        )
        matriculas = GeracadCursoMatricula.search(domain,order=sort_matricula, limit=self._items_per_page,offset=pager['offset'])
        values.update({
            'date': date_begin,
            'matriculas': matriculas.sudo(),
            'page_name': 'matricula',
            'pager': pager,
            'default_url': '/my/matriculas',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        
        return request.render("geracad_curso.portal_my_matriculas", values)


    @http.route(['/my/matriculas/<int:matricula_id>'], type='http', auth="public", website=True)
    def portal_matricula_detail(self, matricula_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            matricula_sudo = self._document_check_access('geracad.curso.matricula', matricula_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=matricula_sudo, report_type=report_type, report_ref='geracad_curso.action_historico_aluno_report', download=download)
        values = self._matricula_get_page_view_values(matricula_sudo, access_token, **kw)
     
        return request.render('geracad_curso.matricula_portal_template', values)


    # ------------------------------------------------------------
    # My Pagamentos
    # ------------------------------------------------------------

    def _pagamentos_get_page_view_values(self, parcela, access_token, **kwargs):
        values = {
            'page_name': 'Pagamentos',
            'parcela': parcela,
            'report_type': 'html',
        }
        return self._get_page_view_values(parcela, access_token, values, 'my_pagamento_history', False, **kwargs)

    def _order_get_page_view_values(self, order, access_token, **kwargs):
        values = {
            'parcela': order,
            'token': access_token,
           
            'bootstrap_formatting': True,
            'aluno_id': order.aluno_id.id,
            'report_type': 'html',
            
        }
        if order.company_id:
            values['res_company'] = order.company_id

        

        
        history = request.session.get('my_pagamentos_history', [])
        values.update(get_records_pager(history, order))

        return values



    #
    # financeiro
    #

    @http.route(['/my/pagamentos', '/my/pagamentos/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_pagamentos(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        GeracadCursoParcelas = request.env['geracad.curso.financeiro.parcelas']

        domain = [
            
            ('aluno_id', '=', partner.id)
        ]

        searchbar_sortings = {
            'date_vencimento': {'label': _('Data Vencimento'), 'order': 'data_vencimento ASC'},
            'date_pagamento': {'label': _('Data Pagamento'), 'order': 'data_pagamento ASC'},
           
            
        }
        # default sortby order
        if not sortby:
            sortby = 'date_vencimento'
        sort_pagamentos = searchbar_sortings[sortby]['order']

        # count for pager
        pagamentos = GeracadCursoParcelas.sudo().search_count(domain)
        
        print("pagametnos_count")
        print(pagamentos)
        
        # make pager
        pager = portal_pager(
            url="/my/pagamentos",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=pagamentos,
            page=page,
            step=self._items_per_page
        )
        parcelas = GeracadCursoParcelas.sudo().search(domain,order=sort_pagamentos, limit=self._items_per_page,offset=pager['offset'])
        values.update({
            'date': date_begin,
            'parcelas': parcelas.sudo(),
            'page_name': 'parcela',
            'pager': pager,
            'default_url': '/my/pagamentos',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        
        
        return request.render("geracad_curso.portal_my_pagamentos", values)


    @http.route(['/my/pagamentos/<int:parcela_id>'], type='http', auth="public", website=True)
    def portal_pagamento_detail(self, parcela_id, report_type=None, access_token=None, message=False, download=False, **kw):
        try:
            parcela_sudo = self._document_check_access('geracad.curso.financeiro.parcelas', parcela_id, access_token=access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=parcela_sudo, report_type=report_type, report_ref='geracad_curso.action_historico_aluno_report', download=download)
        values = self._pagamentos_get_page_view_values(parcela_sudo, access_token, **kw)
     
        return request.render('geracad_curso.matricula_portal_template', values)

    
