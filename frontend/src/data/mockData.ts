// Dados mockados para desenvolvimento/teste
export const mockAreasData = {
  opcoes_areas: {
    'area_1': {
      codigo: '1.1',
      nome: 'Coordenação Geral de Benefícios'
    },
    'area_2': {
      codigo: '1.2', 
      nome: 'Coordenação Geral de Perícias'
    },
    'area_3': {
      codigo: '1.3',
      nome: 'Coordenação Geral de Recursos'
    },
    'area_4': {
      codigo: '2.1',
      nome: 'Coordenação de Atendimento'
    },
    'area_5': {
      codigo: '2.2',
      nome: 'Coordenação de Sistemas'
    },
    'area_6': {
      codigo: '3.1',
      nome: 'Núcleo de Apoio Técnico'
    }
  }
};

export const mockSistemasData = {
  sistemas_por_categoria: {
    'gestao_pessoal': ['SIAPE', 'SIGEP', 'Sistema de Pessoal'],
    'documentos': ['SEI', 'SICOP', 'Arquivo Digital'],
    'previdencia': ['SISBEN', 'CNIS', 'DATAPREV'],
    'transparencia': ['Portal da Transparência', 'e-SIC', 'LAI']
  }
};

export const mockNormasData = {
  sugestoes: [
    {
      nome_curto: 'IN SGP/SEDGG/ME nº 97/2022',
      nome_completo: 'Instrução Normativa sobre Gestão de Benefícios'
    },
    {
      nome_curto: 'Lei 8.112/90',
      nome_completo: 'Regime Jurídico dos Servidores Públicos'
    },
    {
nome_curto: 'Decreto 9.739/2019',
      nome_completo: 'Regulamento sobre Perícias Médicas'
    }
  ]
};

export const mockOperadoresData = {
  opcoes: [
    'Técnico Especializado',
    'Coordenador',
    'Apoio-Gabinete', 
    'Analista Sênior',
    'Supervisor',
    'Perito Médico'
  ]
};