import axios, { AxiosError } from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 300000, // 5 minute timeout
});

// Add response interceptor for logging
api.interceptors.response.use(
    (response) => {
        console.log('API Response:', {
            url: response.config.url,
            status: response.status,
            data: response.data
        });
        return response;
    },
    (error: AxiosError) => {
        console.error('API Error:', {
            url: error.config?.url,
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
        });
        return Promise.reject(error);
    }
);

export interface CompanyData {
    company_info: {
        name: string;
        description: string;
        sector: string;
        industry: string;
    };
    financial_data: {
        [key: string]: any;
    };
    market_data: {
        [key: string]: any;
    };
    financial_analysis: {
        financial_health: string;
        market_position: string;
        growth_potential: string;
        key_metrics_analysis: string;
    };
    potential_risks: string[];
    news_data: Array<{
        title: string;
        description: string;
        url: string;
        publishedAt: string;
    }>;
}

export const analyzeCompany = async (companyName: string): Promise<CompanyData> => {
    const maxRetries = 3;
    let retryCount = 0;

    const executeWithRetry = async (): Promise<CompanyData> => {
        try {
            console.log(`Analyzing company: ${companyName} (Attempt ${retryCount + 1}/${maxRetries})`);
            const response = await api.post<CompanyData>('/api/research', {
                company_name: companyName
            });

            // Transform the response data if needed
            const transformedData: CompanyData = {
                company_info: {
                    name: response.data.company_info?.name || companyName,
                    description: response.data.company_info?.description || '',
                    sector: response.data.company_info?.sector || '',
                    industry: response.data.company_info?.industry || ''
                },
                financial_data: response.data.financial_data || {},
                market_data: response.data.market_data || {},
                financial_analysis: {
                    financial_health: response.data.financial_analysis?.financial_health || '',
                    market_position: response.data.financial_analysis?.market_position || '',
                    growth_potential: response.data.financial_analysis?.growth_potential || '',
                    key_metrics_analysis: response.data.financial_analysis?.key_metrics_analysis || ''
                },
                potential_risks: response.data.potential_risks || [],
                news_data: response.data.news_data || []
            };

            return transformedData;
        } catch (error) {
            if (axios.isAxiosError(error)) {
                const isTimeout = error.code === 'ECONNABORTED' || error.message.includes('timeout');
                if (isTimeout && retryCount < maxRetries - 1) {
                    retryCount++;
                    console.log(`Request timed out, retrying (${retryCount}/${maxRetries})...`);
                    return executeWithRetry();
                }

                const errorMessage = error.response?.data?.detail?.message 
                    || error.response?.data?.detail 
                    || error.message 
                    || 'Failed to analyze company';
                throw new Error(errorMessage);
            }
            throw error;
        }
    };

    return executeWithRetry();
};

export const checkHealth = async () => {
    try {
        const response = await api.get('/api/health');
        return response.data;
    } catch (error) {
        console.error('Health check failed:', error);
        throw new Error('API health check failed');
    }
}; 