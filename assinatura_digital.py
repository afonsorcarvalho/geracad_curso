import logging
import os
import tempfile
from datetime import datetime
from endesive import pdf
from erpbrasil.assinatura.assinatura import Assinatura
from erpbrasil.assinatura.certificado import Certificado

certificado_nfe_caminho = os.environ.get('certificado_nfe_caminho',
                                         'AFONSO_FLAVIO_RIBEIRO_DE_CARVALHO_79159001372_1649778692306164100.pfx')
certificado_nfe_senha = os.environ.get('certificado_nfe_senha',
                                       '182803')

certificado = Certificado(certificado_nfe_caminho, certificado_nfe_senha, raise_expirado=False)
assinador = Assinatura(certificado)
nome_arquivo_pdf = 'pdf_sample_2.pdf'
arquivo = open(nome_arquivo_pdf, 'rb').read()

dados_assinatura = {
        'sigflags': 3,
        'contact': 'KMEE INFORMATICA LTDA',
        'location': 'BR',
        'signingdate': str.encode(
            datetime.utcnow().strftime("%Y%M%d%H%M%S%Z")),
        'reason': 'Teste assinatura',
    }

_logger = logging.getLogger(__name__)

assinatura = assinador.assina_pdf(
        arquivo=arquivo,
        dados_assinatura=dados_assinatura,
    )
file_temp = 'pdf_sample_2_signed.pdf'
with open(file_temp, 'wb') as fp:
    fp.write(arquivo)
    fp.write(assinatura)