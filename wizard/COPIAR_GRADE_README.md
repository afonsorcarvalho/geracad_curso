# Copiar Grade Curricular

## Descrição

Funcionalidade para copiar versões da grade curricular **entre cursos diferentes** ou criar uma nova versão no mesmo curso, permitindo replicar toda a estrutura de disciplinas de uma grade existente.

## Como Usar

### 1. Acessar o Curso
- Navegue até o menu **Cursos**
- Abra o registro do curso desejado

### 2. Abrir o Wizard de Cópia
- No formulário do curso, clique no botão **"Copiar Grade Curricular"** no cabeçalho
- Um wizard será aberto

### 3. Selecionar Configurações

#### Origem:
1. **Curso de Origem**: Selecione de qual curso copiar a grade (pode ser qualquer curso)
2. **Versão da Grade a Copiar**: Selecione qual versão deseja duplicar

#### Destino:
3. **Curso de Destino**: Selecione para qual curso copiar (pode ser o mesmo ou diferente)
4. **Data de Início da Nova Versão**: Defina a data de início (padrão: hoje)
5. **Marcar Versão Original como Obsoleta**: ☑️ Se marcado, a versão original será marcada como obsoleta após a cópia

### 4. Confirmar a Cópia
- Clique em **"Copiar Grade"**
- Uma mensagem de sucesso mostrará:
  - Nome da nova versão criada
  - Total de disciplinas copiadas

## O que é Copiado

✅ **Copiado**:
- Todas as disciplinas da grade
- Período de cada disciplina
- Módulo
- Sequência
- Se é obrigatória ou optativa

❌ **Não Copiado**:
- Disciplinas marcadas como excluídas

## Comportamento

### Validações
- ✅ Verifica se uma versão foi selecionada
- ✅ Verifica se a data de início foi informada
- ✅ Verifica se já existe uma versão com a mesma data de início
- ✅ Impede duplicatas

### Nomenclatura Automática
A nova versão recebe automaticamente o nome no formato:
```
SIGLA_CURSO/ANO_DATA_INICIO
```
Exemplo: `BSI/2025` (se a data for 01/01/2025)

### Opção de Obsolescência
Se marcada a opção "Marcar Versão Original como Obsoleta":
- ✅ A versão original será marcada como `e_obsoleta = True`
- ✅ A nova versão permanece ativa (`e_obsoleta = False`)
- ✅ Útil para substituir grades antigas

## Exemplo de Uso

### Cenário 1: Atualizar Grade do Ano (Mesmo Curso)
```
1. Curso Origem: Sistemas de Informação
2. Versão: "BSI/2024" (10 disciplinas)
3. Curso Destino: Sistemas de Informação
4. Data: 01/01/2025
5. Marcar original como obsoleta: ☑️

Resultado: 
   - BSI/2024: obsoleta ⚠️
   - BSI/2025: ativa ✅ (10 disciplinas copiadas)
```

### Cenário 2: Copiar Grade Entre Cursos Diferentes
```
1. Curso Origem: Análise de Sistemas
2. Versão: "ADS/2024" (8 disciplinas)
3. Curso Destino: Sistemas de Informação
4. Data: 01/01/2025
5. Marcar original como obsoleta: ☐

Resultado:
   Análise de Sistemas:
   - ADS/2024: continua ativa ✅
   
   Sistemas de Informação:
   - BSI/2025: ativa ✅ (8 disciplinas copiadas de ADS)
```

### Cenário 3: Criar Curso Novo Baseado em Outro
```
1. Curso Origem: Engenharia de Software (consolidado)
2. Versão: "ES/2023" (12 disciplinas)
3. Curso Destino: Engenharia da Computação (novo)
4. Data: 01/01/2025

Resultado:
   - Engenharia da Computação inicia com 12 disciplinas
   - Pode editar a nova grade livremente
   - Grade original permanece intacta
```

## Arquivos Técnicos

### Criados
1. `wizard/copiar_grade_wizard.py` - Modelo do wizard
2. `wizard/copiar_grade_wizard.xml` - View do wizard

### Modificados
1. `models/geracad_curso.py` - Método `action_copiar_grade()`
2. `views/geracad_curso_view.xml` - Botão no formulário
3. `wizard/__init__.py` - Import do wizard
4. `__manifest__.py` - Registro do XML
5. `security/ir.model.access.csv` - Permissões

## Permissões de Segurança

Grupos com acesso:
- ✅ `base.group_user` - Usuários autenticados
- ✅ `geracad_curso.group_geracad_curso_secretaria` - Secretaria
- ✅ `base.group_system` - Administradores

## Logs do Sistema

O wizard registra logs informativos:
```python
- "Iniciando cópia da grade curricular: {nome_versao}"
- "Nova versão criada: {nome_nova_versao}"
- "Total de disciplinas copiadas: {quantidade}"
- "Versão original marcada como obsoleta: {nome_versao}"
```

## Observações

- ⚠️ A cópia é irreversível (não há botão "desfazer")
- ⚠️ Certifique-se de selecionar a data correta
- ⚠️ Disciplinas excluídas não são copiadas
- ✅ Após a cópia, você pode editar a nova versão livremente
- ✅ A grade original não é afetada (exceto pela marcação de obsoleta)

