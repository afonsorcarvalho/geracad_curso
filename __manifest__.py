# -*- coding: utf-8 -*-
{
    'name': "Gerenciador de Cursos",

    'summary': """
        Cadastro e visualização dos Cursos""",

    'description': """
        Cadastro e visualização dos Cursos
    """,

    'author': "Netcom Treinamentos e Soluções Tecnológicas",
    'website': "http://www.netcom-ma.com.br",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Academico',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','geracad_aluno'],

    # always loaded
    'data': [
        'security/geracad_curso_security.xml',
        'security/ir.model.access.csv',
        'views/geracad_curso_view.xml',
        'views/geracad_curso_grade_view.xml',
        'views/geracad_curso_disciplina_view.xml',
        'views/res_company.xml',
        'reports/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
