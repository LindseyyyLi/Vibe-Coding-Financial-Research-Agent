export interface FinancialMetrics {
    revenue: string;
    net_income: string;
    total_debt: string;
    cash: string;
    [key: string]: string;
}

export interface CompanyReport {
    company_name: string;
    overview: string;
    financial_metrics: FinancialMetrics;
    potential_risks: string[];
    sources: string[];
}

export interface CompanyRequest {
    company_name: string;
}

export interface ApiError {
    status: number;
    message: string;
} 