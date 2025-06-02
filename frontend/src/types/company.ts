export interface FinancialData {
    revenue: string;
    gross_profit: string;
    operating_margin: string;
    pe_ratio: string;
    market_cap: string;
    price: string;
    change_percent: string;
    volume: string;
    week_52_high: string;
    week_52_low: string;
}

export interface CompanyInfo {
    name: string;
    description: string;
    sector: string;
    industry: string;
}

export interface FinancialAnalysis {
    financial_health: string;
    market_position: string;
    growth_potential: string;
    key_metrics_analysis: string;
}

export interface NewsItem {
    title: string;
    description: string;
    url: string;
    publishedAt: string;
}

export interface CompanyResponse {
    company_info: CompanyInfo;
    financial_data: FinancialData;
    financial_analysis: FinancialAnalysis;
    potential_risks: string[];
    news_data: NewsItem[];
    sources: string[];
}

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