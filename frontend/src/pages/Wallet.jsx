import { useState } from 'react';
import { TrendingUp, Download } from 'lucide-react';
import { mockTransactions } from '../lib/dataMocks';
import WalletStatus from '../components/WalletStatus';
import './Wallet.css';

export default function Wallet() {
  const [balance] = useState(2500);
  const [transactions] = useState(mockTransactions);

  return (
    <div className="wallet-page">
      <h1>Wallet & Balance</h1>

      <WalletStatus balance={balance} onConnect={() => {}} />

      <div className="stats-grid">
        <div className="stat-card">
          <TrendingUp size={24} className="stat-icon" />
          <div>
            <p className="label">Total Earnings</p>
            <p className="value">$3,450.25</p>
          </div>
        </div>
        <div className="stat-card">
          <Download size={24} className="stat-icon" />
          <div>
            <p className="label">Total Spent</p>
            <p className="value">$1,200.50</p>
          </div>
        </div>
      </div>

      <div className="transactions-section">
        <h2>Recent Transactions</h2>
        <div className="transactions-list">
          {transactions.map((tx) => (
            <div key={tx.id} className={`transaction ${tx.type}`}>
              <div className="tx-info">
                <p className="tx-title">
                  {tx.type === 'purchase' ? 'Course Purchase' : ''}
                  {tx.type === 'earnings' ? 'Teaching Earnings' : ''}
                  {tx.type === 'bonus' ? 'Bonus Credit' : ''}
                </p>
                <p className="tx-description">
                  {tx.session || tx.reason || 'N/A'}
                </p>
                <p className="tx-date">
                  {tx.date.toLocaleDateString()}
                </p>
              </div>
              <div className="tx-amount">
                <p className={`amount ${tx.type === 'purchase' ? 'negative' : 'positive'}`}>
                  {tx.type === 'purchase' ? '-' : '+'}${Math.abs(tx.amount).toFixed(2)}
                </p>
                <span className={`status ${tx.status}`}>{tx.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
