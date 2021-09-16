# -*- coding: utf-8 -*-
# from odoo import http


# class GeracadAluno(http.Controller):
#     @http.route('/geracad_aluno/geracad_aluno/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/geracad_aluno/geracad_aluno/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('geracad_aluno.listing', {
#             'root': '/geracad_aluno/geracad_aluno',
#             'objects': http.request.env['geracad_aluno.geracad_aluno'].search([]),
#         })

#     @http.route('/geracad_aluno/geracad_aluno/objects/<model("geracad_aluno.geracad_aluno"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('geracad_aluno.object', {
#             'object': obj
#         })
