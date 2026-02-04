import { Wallet, AlertCircle } from 'lucide-react';
import './WalletStatus.css';

export default function WalletStatus({ balance, onConnect }) {
  return (
    <div className="wallet-status">
      <div className="wallet-info">
        <Wallet size={24} className="wallet-icon" />
        <div>
          <div className="balance-label">Wallet Balance</div>
          <div className="balance-amount">${balance.toFixed(2)}</div>
        </div>
      </div>

      {balance < 50 && (
        <div className="low-balance-warning">
          <AlertCircle size={16} />
          <span>Add funds to continue learning</span>
        </div>
      )}

      <button onClick={onConnect} className="connect-btn">
        + Add Funds
      </button>
    </div>
  );
}
