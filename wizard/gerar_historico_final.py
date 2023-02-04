# © 2019 Raphael Rodrigues, Trustcode
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

from collections import defaultdict

class GeracadCursoGerarHistoricoFinal(models.TransientModel):
    _name = "geracad.curso.gerar.historico.final"
    _description = "Assistente de Finalizar aulas de Turmas de Disciplinas"

  
    matricula_id = fields.Many2one(
        "geracad.curso.matricula",
        string='matricula',
        )
    
    data_conclusao = fields.Date(
        string="Data Conclusão do Curso",
        default=fields.Date.context_today,
    )
    
    disciplina_faltantes_id = fields.One2many(
       "geracad.curso.disciplinas.faltantes.historico.final", 
       inverse_name="gerar_historico_final_id",
       readonly=True, string="Disciplinas Faltantes",
       domain=[('concluida','=',0)]
    )
    disciplina_concluidas_id = fields.One2many(
       "geracad.curso.disciplinas.faltantes.historico.final", 
       inverse_name="gerar_historico_final_id",
       readonly=True, string="Disciplinas Concluídas",
       domain=[('concluida','=',1)]
    )

    def _retorna_index_nota_disciplina_maior_media(self, nota_disciplinas):
        '''
            Recebe uma lista de notas de disciplnas iguais para analise e selecao apenas da de maior media
            Retorna uma lista com o indice e a nota da disciplina de maior media
        '''
        nota=0
        nota_maior=0
        index=0
        for disc in nota_disciplinas:
            if nota_maior <= disc.media:
                nota_maior = disc.media
                nota_disciplinas_maior_nota = disc
                index_maior_nota = index
            index=index+1
        return [index_maior_nota,nota_disciplinas_maior_nota]


    def _limpa_disciplinas_duplicadas(self, nota_disciplinas):
        disciplinas_ids = []
        list_nota_disciplinas = list(nota_disciplinas)
        _logger.info("LIMPANDO ESSAS DISCIPLINAS ABAIXO")
        _logger.info(nota_disciplinas)
        # apenas paga log
        for d in nota_disciplinas:
            _logger.info(str(d.disciplina_id.id) + '-' + str(d.disciplina_id.codigo) + ' ' + str(d.disciplina_id.name))
        
        # pegando apenas os ids das disciplinas, para saber quais estao duplicadas
        disciplinas_ids = list(map(lambda x: x.disciplina_id.id, nota_disciplinas))

        # Define o objeto que armazenará os índices de cada elemento:
        keys = defaultdict(list)

        # Percorre todos os elementos da lista:
        for key, value in enumerate(disciplinas_ids):
            # Adiciona o índice do valor na lista de índices:
            keys[value].append(key)

        
        nota_disciplinas_duplicadas_limpas = []
        for value in keys:
            if len(keys[value]) > 1:
                print(value, keys[value])
                lista_notas_duplicadas = []

                for index in keys[value]:
                    # notas duplicadas
                    lista_notas_duplicadas.append(nota_disciplinas[index])
                # escolhe a de maior média
                nota_disciplina_maior_media = self._retorna_index_nota_disciplina_maior_media(lista_notas_duplicadas)

                # retirar usada apenas para debugagem 
                nota_disciplinas_duplicadas_limpas.append(nota_disciplina_maior_media[1])

                # removendo a de maior media, deixando apenas a lista de indices a serem apagados 
                keys[value].pop(nota_disciplina_maior_media[0])
                _logger.info("indices a serem apagados")
                _logger.info(keys[value])
                # apagando da lista de notas de disciplinas os duplicados com menores médias
                
                for index in keys[value]:
                    list_nota_disciplinas.pop(index)

               
        _logger.info("DISCIPLINAS LIMPAS DE DUPLICIDADE") 
        for d in list_nota_disciplinas:
            _logger.info(str(d.disciplina_id.id) + '-' + str(d.disciplina_id.codigo) + ' ' + str(d.disciplina_id.name) + ' MEDIA=' + str(d.media ))

        return list_nota_disciplinas

    
    def _gera_nota_historico_final_aluno(self):
        _logger.info("GERANDO NOTAS DO HISTÓRICO FINAL")
        nota_disciplina_ids = self.env['geracad.curso.nota.disciplina'].search([
            '&',
            ('curso_matricula_id','=',self.matricula_id.id),
            ('situation','in',['AM','AP','EA']),
            ('state', 'not in',['cancelada'])
            ])
        nota_disciplinas_sem_duplicidade = self._limpa_disciplinas_duplicadas(nota_disciplina_ids)
        _logger.info("nota_disciplinas_sem_duplicidade")
        _logger.info(nota_disciplinas_sem_duplicidade)
        for nota_disciplina in nota_disciplina_ids:
            _logger.info(nota_disciplina.disciplina_matricula_id)
            self.env['geracad.curso.nota.disciplina.historico.final'].create({
                'disciplina_matricula_id': nota_disciplina.disciplina_matricula_id.id,
                'periodo': nota_disciplina.periodo,
                'faltas': nota_disciplina.faltas,
                'nota_1': nota_disciplina.nota_1,
                'nota_2': nota_disciplina.nota_2,
                'final': nota_disciplina.final,
                'media': nota_disciplina.media,
                'carga_horaria': nota_disciplina.disciplina_id.carga_horaria,
                'situation': nota_disciplina.situation,
                'state': 'concluida'

            }
            )
        

   

    def action_confirm(self):
        """
        
        """
        _logger.debug("Confirmado Geração de Histórico Final")
        if len(self.disciplina_faltantes_id) > 0:
           raise UserError(_('O histórico final só poderá ser gerado caso o aluno tenha todas as disciplinas do curso concluídas e aprovadas.'))
        self._gera_nota_historico_final_aluno()

        self.matricula_id.write({
            'data_conclusao': self.data_conclusao,
            'state': 'formado'
            })    
        
    

class GeracadCursoDisciplinasFaltantesHistoricoFinal(models.TransientModel):
    _name = "geracad.curso.disciplinas.faltantes.historico.final"
    _description = "Disciplinas Faltantes histórico Final"

  
    gerar_historico_final_id = fields.Many2one(
       "geracad.curso.gerar.historico.final",
     
        )
        
    disciplina_id =  fields.Many2one(
       
        "geracad.curso.disciplina", string="Disciplinas"
    )
    carga_horaria =  fields.Integer(        
        related='disciplina_id.carga_horaria',
        readonly=True,
    )
    metodologia =  fields.Many2one(        
        related='disciplina_id.metodologia',
        readonly=True,
    )
    concluida = fields.Boolean(
       
         string="Concluída"
    )
    
