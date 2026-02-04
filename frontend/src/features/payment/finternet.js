// Mock Finternet payment service
export const finternet = {
  async connectWallet() {
    // Mock wallet connection
    return { address: '0x1234...5678', balance: 2500 };
  },

  async getBalance(address) {
    // Mock get balance
    return 2500;
  },

  async initiatePayment(amount, sessionId) {
    // Mock payment initiation
    return { transactionId: 'tx_' + Date.now(), status: 'pending' };
  },

  async settlePayment(transactionId) {
    // Mock payment settlement
    return { status: 'completed', transactionId };
  },

  async getTransactionHistory(address) {
    // Mock transaction history
    return [];
  },

  async estimateSessionCost(durationMinutes, pricePerMinute) {
    return durationMinutes * pricePerMinute;
  },
};
