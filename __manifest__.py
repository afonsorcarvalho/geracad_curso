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
    'depends': [
        'base',
        'geracad_aluno', 
        'portal',
        'mail',
        'web_domain_field',
        'web_dialog_size',
        'web_calendar_color_field',
        'web_view_calendar_list',
        'web_widget_open_tab',
        ],

    # always loaded
    'data': [
        'security/geracad_curso_security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/mail_template.xml',
        'views/geracad_curso_contrato_view.xml',
        'views/geracad_curso_grade_view.xml',
        'views/geracad_curso_disciplina_view.xml',
        'views/geracad_curso_equivalencia_disciplina_view.xml',
        'views/geracad_curso_turma_disciplina_view.xml',
        'views/geracad_curso_turma_disciplina_aulas_view.xml',
        'views/geracad_curso_matricula_disciplina_view.xml',
        'views/geracad_curso_matricula_view.xml',
        'views/geracad_curso_nota_disciplina_view.xml',
        'views/geracad_curso_nota_disciplina_aproveitamento_view.xml',
        'views/geracad_curso_financeiro_parcelas_view.xml',
        'views/geracad_curso_professores_view.xml',
        'views/geracad_curso_view.xml',
        'views/geracad_curso_nota_disciplina_historico_final_view.xml',
        'views/alunos_view.xml',
        'views/res_company.xml',
        'views/portal_templates.xml',
        'views/geracad_curso_portal_templates.xml',
        'reports/report_contrato_aluno_template.xml',
        'reports/report_declaracao_aluno_template.xml',
        'reports/report_historico_aluno_notas_template.xml',
        #'reports/report_historico_aluno_notas_antigo_template.xml',
        'reports/report_historico_aluno_template.xml',
        #'reports/report_historico_aluno_antigo_template.xml',
        'reports/report_disciplinas_pendentes_aluno_template.xml',
        'reports/report_historico_disciplinas_pendentes_aluno_template.xml',
        'reports/report_turma_disciplina_diario_template.xml',
        'reports/report_turma_disciplina_diario_final_template.xml',
        'reports/report_turma_disciplina_ata_avaliacao_template.xml',
        'reports/report_turma_disciplina_ata_frequencia_avaliacao_template.xml',
        'reports/report_turma_disciplina_ata_frequencia_aula_template.xml',
        'reports/report_recibo_parcela_template.xml',
        'reports/report_pendencias_financeira_aluno_template.xml',
        'reports/report_pendencias_financeira_turma_template.xml',
        'reports/report_ata_resultados_template.xml',
        'reports/report_mapa_pagamento_turma_template.xml',
        'reports/report_actions.xml',
        'wizard/pagamento_parcela.xml',
        'wizard/finalizar_aula.xml',
        'wizard/gerar_historico_final.xml',
        'wizard/pendencias_financeira_aluno_wizard.xml',
        'wizard/pendencias_financeira_por_turma_wizard.xml',
        'wizard/curso_ata_resultados_wizard.xml',
        'wizard/curso_mapa_pagamento_wizard.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
