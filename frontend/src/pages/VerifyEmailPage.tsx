import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { verifyEmailApi } from '../services/authApi';

export default function VerifyEmailPage() {
  const { uid, token } = useParams<{ uid: string; token: string }>();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');
  const [accessStatus, setAccessStatus] = useState('');

  useEffect(() => {
    if (!uid || !token) {
      setStatus('error');
      setMessage('Link invalido.');
      return;
    }

    verifyEmailApi(uid, token)
      .then(data => {
        setStatus('success');
        setMessage(data.mensagem);
        setAccessStatus(data.access_status);
      })
      .catch(err => {
        setStatus('error');
        setMessage(err.response?.data?.erro || 'Erro ao verificar email.');
      });
  }, [uid, token]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f4f6f9' }}>
      <div style={{ width: '100%', maxWidth: 480, padding: 32, background: '#fff', borderRadius: 8, boxShadow: '0 2px 8px rgba(0,0,0,0.1)', textAlign: 'center' }}>
        {status === 'loading' && (
          <p style={{ color: '#666' }}>Verificando email...</p>
        )}

        {status === 'success' && (
          <>
            <h2 style={{ color: '#1B4F72', marginBottom: 16 }}>Email verificado</h2>
            <p style={{ color: '#333', marginBottom: 16 }}>{message}</p>
            {accessStatus === 'approved' ? (
              <>
                <p style={{ color: '#2e7d32', fontWeight: 500 }}>Acesso liberado!</p>
                <Link to="/sobre" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Conhecer o MapaGov</Link>
              </>
            ) : (
              <>
                <p style={{ color: '#666', fontSize: 14 }}>
                  Seu cadastro esta em analise pela equipe responsavel.
                  Voce sera avisado por email quando o acesso for liberado.
                </p>
                <Link to="/sobre" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Conhecer o MapaGov</Link>
              </>
            )}
          </>
        )}

        {status === 'error' && (
          <>
            <h2 style={{ color: '#b71c1c', marginBottom: 16 }}>Erro na verificacao</h2>
            <p style={{ color: '#333', marginBottom: 16 }}>{message}</p>
            <Link to="/login" style={{ color: '#1351B4', textDecoration: 'none', fontWeight: 500 }}>Voltar ao login</Link>
          </>
        )}
      </div>
    </div>
  );
}
