import { useEffect, useState } from 'react';
import { listPendingUsers, castVote } from '../services/adminApi';
import type { PendingUser, VoteResult } from '../services/adminApi';

export default function AdminUsersPage() {
  const [users, setUsers] = useState<PendingUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [votingId, setVotingId] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  const loadUsers = async () => {
    setLoading(true);
    try {
      const data = await listPendingUsers();
      setUsers(data);
    } catch {
      setMessage('Erro ao carregar usuarios.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadUsers(); }, []);

  const handleVote = async (userId: number, vote: 'approve' | 'reject') => {
    setVotingId(userId);
    setMessage('');
    try {
      const result: VoteResult = await castVote(userId, vote);
      setMessage(result.mensagem);
      if (result.result) {
        setMessage(`${result.mensagem} Status final: ${result.access_status}`);
      }
      loadUsers();
    } catch (err: any) {
      setMessage(err.response?.data?.erro || 'Erro ao registrar voto.');
    } finally {
      setVotingId(null);
    }
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 20px' }}>
      <h1 style={{ color: '#1B4F72', marginBottom: 8 }}>Cadastros pendentes</h1>
      <p style={{ color: '#666', marginBottom: 24 }}>Usuarios externos aguardando aprovacao de acesso.</p>

      {message && (
        <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '10px 14px', borderRadius: 4, marginBottom: 16 }}>
          {message}
        </div>
      )}

      {loading ? (
        <p style={{ color: '#666' }}>Carregando...</p>
      ) : users.length === 0 ? (
        <p style={{ color: '#666' }}>Nenhum cadastro pendente no momento.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {users.map(user => (
            <div key={user.id} style={{ border: '1px solid #ddd', borderRadius: 8, padding: 20, background: '#fff' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ margin: 0, color: '#1B4F72' }}>{user.nome_completo || user.username}</h3>
                  <p style={{ margin: '4px 0', color: '#666', fontSize: 14 }}>{user.email}</p>
                  {user.cargo && <p style={{ margin: '2px 0', color: '#888', fontSize: 13 }}>Cargo: {user.cargo}</p>}
                  <p style={{ margin: '2px 0', color: '#888', fontSize: 13 }}>
                    Cadastro: {new Date(user.created_at).toLocaleDateString('pt-BR')}
                    {user.email_verified ? ' — Email verificado' : ' — Email nao verificado'}
                  </p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span style={{ fontSize: 13, color: '#666' }}>
                    {user.approvals_count}/3 aprovacoes | {user.rejections_count}/2 rejeicoes
                  </span>
                </div>
              </div>

              {user.votes.length > 0 && (
                <div style={{ marginTop: 12, padding: '8px 12px', background: '#f5f5f5', borderRadius: 4 }}>
                  <p style={{ fontSize: 12, fontWeight: 600, color: '#666', marginBottom: 4 }}>Votos:</p>
                  {user.votes.map((v, i) => (
                    <p key={i} style={{ fontSize: 12, color: v.vote === 'approve' ? '#2e7d32' : '#b71c1c', margin: '2px 0' }}>
                      {v.admin_email} — {v.vote === 'approve' ? 'Aprovado' : 'Rejeitado'}
                      {v.justificativa && ` (${v.justificativa})`}
                    </p>
                  ))}
                </div>
              )}

              <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
                <button
                  onClick={() => handleVote(user.id, 'approve')}
                  disabled={votingId === user.id}
                  style={{
                    padding: '8px 20px', background: '#2e7d32', color: '#fff',
                    border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 500,
                  }}
                >
                  Aprovar
                </button>
                <button
                  onClick={() => handleVote(user.id, 'reject')}
                  disabled={votingId === user.id}
                  style={{
                    padding: '8px 20px', background: '#b71c1c', color: '#fff',
                    border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 500,
                  }}
                >
                  Rejeitar
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
