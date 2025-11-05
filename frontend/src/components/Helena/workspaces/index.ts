/**
 * Workspaces - Componentes visuais para cada modelo de Planejamento Estratégico
 * Baseados em metodologias do MGI/MPO para setor público
 */

export { WorkspaceSWOT } from './WorkspaceSWOT';
export { WorkspaceOKR } from './WorkspaceOKR';
export { WorkspaceBSC } from './WorkspaceBSC';
export { Workspace5W2H } from './Workspace5W2H';

// Tipos de dados para cada workspace
export type { DadosSWOT, ItemSWOT } from './WorkspaceSWOT';
export type { DadosOKR, Objetivo as ObjetivoOKR, KeyResult } from './WorkspaceOKR';
export type { DadosBSC, Perspectiva, Objetivo as ObjetivoBSC, Indicador } from './WorkspaceBSC';
export type { Dados5W2H, Acao } from './Workspace5W2H';
