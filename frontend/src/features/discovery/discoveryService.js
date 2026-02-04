import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const discoveryService = {
    // Fetch lists of public listings (for Home/Feed)
    async getListings({ limit = 50, tag } = {}) {
        try {
            const params = { limit };
            if (tag) params.tag = tag;

            const response = await api.get('/discovery/listings', { params });
            return response.data;
        } catch (error) {
            console.error('Error fetching listings:', error);
            throw error;
        }
    },

    // Fetch details for a single listing (for Course Detail page)
    async getListingDetail(listingId) {
        try {
            const response = await api.get(`/discovery/listings/${listingId}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching listing ${listingId}:`, error);
            throw error;
        }
    },

    // AI Suggestion (Search)
    async suggest(query) {
        try {
            const response = await api.post('/discovery/suggest', { query });
            return response.data;
        } catch (error) {
            console.error('Error getting suggestions:', error);
            throw error;
        }
    }
};
