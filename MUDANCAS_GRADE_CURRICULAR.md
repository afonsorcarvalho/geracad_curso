# Mudanças - Relatório de Grade Curricular

## Resumo
Foi implementado um relatório completo de grade curricular com seleção de versão através de wizard.

## Arquivos Modificados

1. **wizard/wizard_print_grade.py** - Corrigido e documentado
2. **wizard/wizard_print_grade.xml** - Corrigido campos da view
3. **wizard/__init__.py** - Adicionado import do wizard
4. **models/geracad_curso.py** - Atualizado método action_open_wizard_print_report()
5. **views/geracad_curso_view.xml** - Adicionado botão "Imprimir Grade Curricular"
6. **reports/report_actions.xml** - Corrigido action do relatório
7. **security/ir.model.access.csv** - Adicionadas permissões para o wizard
8. **__manifest__.py** - Registrados novos arquivos XML

## Arquivos Criados

1. **reports/report_grade_curricular_template.xml** - Template do relatório
2. **reports/DOCUMENTACAO_GRADE_CURRICULAR.md** - Documentação completa

## Para Ativar

Execute no terminal dentro do container Odoo:
```bash
# Atualizar o módulo
odoo-bin -u geracad_curso -d nome_do_banco --stop-after-init
```

Ou via interface web:
1. Ative o modo desenvolvedor
2. Vá em Apps/Aplicativos
3. Procure "Gerenciador de Cursos"
4. Clique em "Atualizar"

## Como Testar

### Método 1: A partir de um Curso
1. Abra qualquer curso cadastrado
2. Clique no botão "Imprimir Grade Curricular" no cabeçalho OU clique em "Imprimir" e escolha "Grade Curricular"
3. O curso já virá preenchido
4. Selecione uma versão da grade
5. Clique em "Imprimir"
6. Visualize o PDF gerado

### Método 2: Selecionando Curso e Versão
1. Acesse o wizard de impressão de grade curricular
2. Selecione o curso desejado
3. Selecione a versão da grade (o campo aparecerá após selecionar o curso)
4. Clique em "Imprimir"
5. Visualize o PDF gerado

## Permissões Configuradas

O wizard possui permissões para:
- Usuários autenticados (base.group_user)
- Secretaria (geracad_curso.group_geracad_curso_secretaria)
- Secretaria Read-only (geracad_curso.group_geracad_curso_secretaria_only_read)
- Administradores (base.group_system)

## Observações

- O relatório é gerado em PDF
- Disciplinas são organizadas por períodos
- Mostra código, nome, carga horária e tipo de cada disciplina
- Inclui subtotais por período e total geral
- Design profissional e responsivo

