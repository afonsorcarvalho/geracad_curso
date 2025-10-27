# Documentação - Relatório de Grade Curricular

## Descrição

Este módulo implementa um relatório para impressão da grade curricular de cursos, permitindo ao usuário selecionar qual versão da grade deseja visualizar/imprimir.

## Funcionalidades

### 1. Wizard de Seleção
- Permite selecionar a versão da grade curricular antes de gerar o relatório
- Filtra automaticamente apenas as versões do curso selecionado
- Validação para garantir que uma versão seja selecionada antes de imprimir

### 2. Relatório de Grade Curricular

O relatório exibe as seguintes informações:

#### Cabeçalho
- Nome do curso
- Resolução do curso (se disponível)
- Versão da grade selecionada
- Data de início da versão
- Modalidade do curso
- Tipo do curso

#### Disciplinas Organizadas por Período
As disciplinas são agrupadas e exibidas por período, mostrando:
- **Código da Disciplina**: Código único da disciplina
- **Nome da Disciplina**: Nome completo da disciplina
- **Carga Horária**: Carga horária em horas
- **Metodologia**: Tipo de metodologia da disciplina (ex: Teórica, Prática, Teórico-Prática)
- **Tipo**: Se é obrigatória ou optativa

#### Informações Adicionais
- Subtotal de carga horária por período
- Carga horária total do curso
- Data e hora de geração do documento

## Como Usar

### Método 1: A partir de um Curso específico

#### Passo 1: Acessar o Curso
1. Navegue até o menu **Cursos**
2. Abra o registro do curso desejado

#### Passo 2: Abrir o Wizard
Você tem duas opções:
- **Opção A**: Clique no botão **"Imprimir Grade Curricular"** no cabeçalho do formulário
- **Opção B**: Clique no botão **"Imprimir"** (ícone de impressora) e selecione **"Grade Curricular"**

#### Passo 3: Selecionar a Versão
1. No wizard, o campo **Curso** já estará preenchido automaticamente
2. Selecione a **Versão da Grade** desejada no campo dropdown
3. Clique em **"Imprimir"**

### Método 2: Escolhendo Curso e Versão

#### Passo 1: Abrir o Wizard Diretamente
1. Acesse o menu de impressão de qualquer curso OU
2. Use a opção de menu (se configurada)

#### Passo 2: Selecionar Curso e Versão
1. Selecione o **Curso** desejado no primeiro dropdown
2. Após selecionar o curso, o campo **Versão da Grade** ficará visível
3. Selecione a **Versão da Grade** desejada
4. O botão **"Imprimir"** aparecerá quando ambos os campos estiverem preenchidos
5. Clique em **"Imprimir"**

#### Passo 3: Visualizar o Relatório
1. O relatório será gerado em formato PDF
2. Você pode visualizar, imprimir ou salvar o arquivo

## Estrutura Técnica

### Arquivos Criados/Modificados

1. **wizard/wizard_print_grade.py**
   - Modelo transiente para o wizard de seleção
   - Campos: curso_id, grade_versao
   - Métodos: print_grade(), action_confirm()

2. **wizard/wizard_print_grade.xml**
   - View do wizard
   - Action window para abrir o wizard

3. **reports/report_grade_curricular_template.xml**
   - Template QWeb do relatório
   - Formato de página customizado
   - Estilos CSS para apresentação

4. **reports/report_actions.xml**
   - Registro do relatório no sistema
   - Configurações de impressão

5. **models/geracad_curso.py**
   - Método action_open_wizard_print_report() para abrir o wizard

6. **views/geracad_curso_view.xml**
   - Botão adicionado no formulário do curso

7. **security/ir.model.access.csv**
   - Permissões de acesso para o wizard
   - Acesso para: usuários, secretaria, secretaria read-only e administradores

### Modelos Utilizados

- **geracad.curso**: Curso principal
- **geracad.curso.grade.versao**: Versão da grade curricular
- **geracad.curso.grade**: Itens da grade (disciplinas por período)
- **geracad.curso.disciplina**: Informações das disciplinas
- **geracad.curso.wizard.print.grade**: Wizard para seleção da versão

## Layout do Relatório

### Características Visuais
- Cabeçalho centralizado com destaque
- Títulos de período com fundo azul
- Tabela zebrada (linhas alternadas) para melhor legibilidade
- Disciplinas obrigatórias em verde
- Disciplinas optativas em laranja
- Totais destacados em cinza
- Design responsivo e profissional

### Organização das Disciplinas
- As disciplinas são ordenadas por período (ordem crescente)
- **Estágios**: Disciplinas onde `e_estagio = True` são exibidas no final como "Estágio Supervisionado / Atividades Complementares", independentemente do período configurado
- Disciplinas excluídas não são exibidas no relatório
- Cada período mostra seu subtotal de carga horária no cabeçalho
- Layout compacto otimizado para caber em uma página A4

## Observações

- O relatório é gerado em formato PDF por padrão
- As disciplinas marcadas como excluídas (e_excluida=True) não aparecem no relatório
- O formato de página é A4 em orientação retrato (Portrait)
- Todas as strings estão em português brasileiro
- O código está documentado seguindo as boas práticas do Odoo

## Manutenção

Para modificar o layout do relatório, edite o arquivo:
```
addons/geracad_curso/reports/report_grade_curricular_template.xml
```

Para modificar a lógica do wizard, edite o arquivo:
```
addons/geracad_curso/wizard/wizard_print_grade.py
```

## Requisitos

- Odoo 14.0 ou superior
- Módulo geracad_curso instalado e atualizado
- Permissões adequadas para visualizar cursos e gerar relatórios

## Permissões de Segurança

O wizard de impressão de grade curricular possui as seguintes permissões configuradas:

- **base.group_user**: Todos os usuários autenticados podem ler, escrever, criar e excluir (1,1,1,1)
- **geracad_curso.group_geracad_curso_secretaria**: Grupo secretaria com acesso completo (1,1,1,1)
- **geracad_curso.group_geracad_curso_secretaria_only_read**: Grupo secretaria read-only com acesso completo ao wizard (1,1,1,1)
- **base.group_system**: Administradores com acesso completo (1,1,1,1)

**Nota**: Como o wizard é um modelo transiente (TransientModel), ele não persiste dados no banco de dados, sendo seguro conceder permissões completas aos grupos que precisam gerar relatórios.

